# run.py - Just starts things
from app import create_app
from extensions import db  # Import your db instance

app = create_app()

# Create tables on startup (safe for production - won't recreate existing tables)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
    