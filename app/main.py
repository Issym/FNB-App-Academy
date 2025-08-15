from __future__ import annotations
from fastapi import FastAPI, Depends, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from typing import Optional
from uuid import uuid4

from .db import init_db, get_session
from .models import Product, Cart, CartItem, Order, OrderItem
from .promos import apply_promos
from .utils import VAT_RATE, SHIPPING_FLAT, FREE_SHIPPING_THRESHOLD, money

app = FastAPI(title="Week 8 Shopping Cart")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def on_startup():
    init_db()

def get_or_create_cart(request: Request, session: Session) -> Cart:
    cart_key = request.cookies.get("cart_id")
    cart: Optional[Cart] = None
    if cart_key:
        cart = session.exec(select(Cart).where(Cart.cart_key == cart_key)).first()
    if not cart:
        cart = Cart(cart_key=str(uuid4()))
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart

def cart_lines(cart: Cart, session: Session):
    q = select(CartItem, Product).where(CartItem.cart_id == cart.id).join(Product, CartItem.product_id == Product.id)
    rows = session.exec(q).all()
    lines = []
    for ci, p in rows:
        lines.append({
            "product_id": p.id, "sku": p.sku, "name": p.name, "unit_price": p.price, "qty": ci.qty,
            "line_total": round(p.price * ci.qty, 2)
        })
    return lines

def compute_totals(cart: Cart, session: Session):
    lines = cart_lines(cart, session)
    subtotal = round(sum(l["line_total"] for l in lines), 2)
    shipping = 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FLAT
    discount, ship_disc, messages = apply_promos(cart.promos(), subtotal, lines, shipping)
    shipping = max(0.0, shipping - ship_disc)
    taxable = max(0.0, subtotal - discount)
    vat = round(taxable * VAT_RATE, 2)
    grand = round(taxable + vat + shipping, 2)
    return {
        "lines": lines,
        "subtotal": subtotal,
        "discount": discount,
        "vat": vat,
        "shipping": shipping,
        "grand_total": grand,
        "messages": messages,
        "promos": sorted(list(cart.promos())),
    }

# Pages
@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session), q: Optional[str] = None, category: Optional[str] = None):
    stmt = select(Product)
    products = session.exec(stmt).all()
    if q:
        ql = q.lower()
        products = [p for p in products if ql in p.name.lower() or ql in p.sku.lower()]
    if category:
        products = [p for p in products if category.lower() in {c.lower() for c in p.categories()}]
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "q": q or "", "category": category or ""})

@app.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request, session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    totals = compute_totals(cart, session)
    return templates.TemplateResponse("cart.html", {"request": request, "cart": cart, "t": totals, "money": money})

@app.post("/cart/add")
def add_to_cart(request: Request, response: Response, sku: str = Form(...), qty: int = Form(...), session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    product = session.exec(select(Product).where(Product.sku == sku)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ci = session.exec(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)).first()
    new_qty = qty + (ci.qty if ci else 0)
    if new_qty <= 0:
        if ci:
            session.delete(ci); session.commit()
    else:
        if new_qty > product.stock:
            raise HTTPException(status_code=400, detail=f"Not enough stock (max {product.stock})")
        if ci:
            ci.qty = new_qty
        else:
            ci = CartItem(cart_id=cart.id, product_id=product.id, qty=new_qty)
            session.add(ci)
        session.commit()

    resp = RedirectResponse(url="/cart", status_code=303)
    if "cart_id" not in request.cookies:
        resp.set_cookie("cart_id", cart.cart_key, httponly=True, samesite="lax")
    return resp

@app.post("/cart/set")
def set_qty(request: Request, response: Response, sku: str = Form(...), qty: int = Form(...), session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    product = session.exec(select(Product).where(Product.sku == sku)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ci = session.exec(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)).first()
    if not ci:
        raise HTTPException(status_code=404, detail="Item not in cart")
    if qty <= 0:
        session.delete(ci)
    else:
        if qty > product.stock:
            raise HTTPException(status_code=400, detail=f"Not enough stock (max {product.stock})")
        ci.qty = qty
    session.commit()
    return RedirectResponse(url="/cart", status_code=303)

@app.post("/cart/promo")
def apply_promo(request: Request, code: str = Form(...), session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    code = (code or "").strip().upper()
    promos = cart.promos()
    promos.add(code)
    cart.promo_csv = ",".join(sorted(promos))
    session.add(cart); session.commit()
    return RedirectResponse(url="/cart", status_code=303)

@app.post("/checkout")
def checkout(request: Request, session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    totals = compute_totals(cart, session)
    if not totals["lines"]:
        return RedirectResponse(url="/", status_code=303)

    order = Order(
        total_ex_vat=totals["subtotal"] - totals["discount"],
        discount=totals["discount"],
        vat=totals["vat"],
        shipping=totals["shipping"],
        grand_total=totals["grand_total"],
        promo_csv=",".join(totals["promos"]),
    )
    session.add(order); session.commit(); session.refresh(order)
    for l in totals["lines"]:
        oi = OrderItem(
            order_id=order.id,
            product_id=l["product_id"],
            sku=l["sku"],
            name=l["name"],
            unit_price=l["unit_price"],
            qty=l["qty"],
            line_total=l["line_total"],
        )
        session.add(oi)
        # reduce stock
        prod = session.get(Product, l["product_id"])
        if prod:
            prod.stock = max(0, prod.stock - l["qty"])
    # clear cart
    session.exec(select(CartItem).where(CartItem.cart_id == cart.id))
    for item in list(cart.items):
        session.delete(item)
    cart.promo_csv = ""
    session.commit()

    return RedirectResponse(url=f"/checkout/success/{order.id}", status_code=303)

@app.get("/checkout/success/{order_id}", response_class=HTMLResponse)
def success(order_id: int, request: Request, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("checkout_success.html", {"request": request, "order": order, "money": money})

# Simple JSON API
@app.get("/api/products")
def api_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

@app.get("/api/cart")
def api_cart(request: Request, session: Session = Depends(get_session)):
    cart = get_or_create_cart(request, session)
    return compute_totals(cart, session)
