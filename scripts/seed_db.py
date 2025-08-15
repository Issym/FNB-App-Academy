import json
from pathlib import Path
from sqlmodel import Session
from app.db import init_db, engine
from app.models import Product

DATA = Path(__file__).resolve().parent.parent / "data" / "products.json"

def main():
    init_db()
    with open(DATA, "r", encoding="utf-8") as f:
        raw = json.load(f)
    with Session(engine) as s:
        # idempotent insert
        for sku, d in raw.items():
            exists = s.exec(Product.select().where(Product.sku == sku)).first() if hasattr(Product, "select") else None
            if not exists:
                p = Product(sku=sku, name=d["name"], price=float(d["price"]), stock=int(d["stock"]), categories_csv=",".join(d["categories"]))
                s.add(p)
        s.commit()
    print("✅ Seed complete.")

if __name__ == "__main__":
    main()
