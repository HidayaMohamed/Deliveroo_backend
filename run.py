from app import create_app
from extensions import db

app = create_app()

# Seed data ONCE on startup (safe - idempotent)
try:
    with app.app_context():
        db.create_all()
        from seed import seed_data
        seed_data()
    print("✅ Database seeded with production data!")
except Exception as e:
    print(f"⚠️ Seeding skipped (already done): {e}")

if __name__ == '__main__':
    app.run(debug=True)


    