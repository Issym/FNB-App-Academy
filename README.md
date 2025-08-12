# Contact Book API (Flask)

A clean, beginner-friendly REST API for managing contacts, built with **Flask**, **SQLAlchemy**, and **JWT auth**.
Perfect for App Academy Week 7's "Build your own backend API (Contact Book)" lesson.

---

## Quick Start

```bash
# 0) (Optional) Create & activate a virtualenv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 1) Install dependencies
pip install -r requirements.txt

# 2) Setup environment
cp .env.example .env   # or copy manually on Windows
# (edit .env if you want a different DB path or port)

# 3) Initialize the database (creates contactbook.db with tables)
python scripts/init_db.py

# 4) Run the server
python app.py
# or: flask --app app.py run --debug
```

Server starts at: **http://127.0.0.1:5000** (default from `.env`)

> Tip: If your cohort uses an API key or email for demos, you can ignore it here—this API uses JWT tokens returned by `/api/login`.

---

## API Overview

All endpoints are prefixed with `/api`.

### Auth
- `POST /api/register` — Create a user account
- `POST /api/login` — Get a JWT access token
- `GET /api/me` — Get the current user (requires `Authorization: Bearer <token>`)

### Contacts (all require Auth)
- `GET /api/contacts` — List (supports `q` search, `page`, `per_page`)
- `POST /api/contacts` — Create
- `GET /api/contacts/<id>` — Read one
- `PUT /api/contacts/<id>` — Update
- `DELETE /api/contacts/<id>` — Delete

### Contact JSON shape
```json
{
  "id": 1,
  "name": "Ada Lovelace",
  "phone": "+27 82 000 0000",
  "email": "ada@example.com",
  "address": "Durban, SA",
  "created_at": "2025-08-12T10:00:00Z"
}
```

---

## cURL Examples

```bash
# Register
curl -X POST http://127.0.0.1:5000/api/register   -H "Content-Type: application/json"   -d '{"name":"Ishmael","email":"ishmael@example.com","password":"Passw0rd!"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/login   -H "Content-Type: application/json"   -d '{"email":"ishmael@example.com","password":"Passw0rd!"}' |   python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create contact
curl -X POST http://127.0.0.1:5000/api/contacts   -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"   -d '{"name":"Ada Lovelace","phone":"+27 82 123 4567","email":"ada@example.com","address":"Durban"}'

# List contacts (search & pagination)
curl -H "Authorization: Bearer $TOKEN"   "http://127.0.0.1:5000/api/contacts?q=ada&page=1&per_page=10"

# Update
curl -X PUT http://127.0.0.1:5000/api/contacts/1   -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"   -d '{"phone":"+27 82 000 0000"}'

# Delete
curl -X DELETE http://127.0.0.1:5000/api/contacts/1   -H "Authorization: Bearer $TOKEN"
```

---

## Postman
Import `postman/ContactBook.postman_collection.json` and set the `baseUrl` to your server (default `http://127.0.0.1:5000`).

---

## Project Structure
```
contact-book-api/
├─ app.py                 # Application entry point
├─ config.py              # Config from environment
├─ db.py                  # SQLAlchemy instance
├─ models.py              # User & Contact models
├─ auth.py                # Auth blueprint (register/login/me)
├─ contacts.py            # Contacts CRUD blueprint
├─ requirements.txt
├─ .env.example           # Sample environment variables
├─ scripts/
│  └─ init_db.py         # Create tables
└─ postman/
   └─ ContactBook.postman_collection.json
```
