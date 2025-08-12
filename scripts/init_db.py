from dotenv import load_dotenv
from app import create_app
from db import db

def main():
    load_dotenv()
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database initialized (tables created).")

if __name__ == "__main__":
    main()
