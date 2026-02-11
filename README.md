# Deliveroo Backend

## Quick Start

### 1. Install Dependencies
```bash
pip install pipenv
pipenv install
```

### 2. Configure PostgreSQL

Run the setup script:
```bash
chmod +x setup_postgres.sh
./setup_postgres.sh
```

Or manually:
```bash
# Set password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Create database
sudo -u postgres createdb deliveroo
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (DATABASE_URL already configured)
```

### 4. Run Migrations
```bash
flask db upgrade
```

### 5. Start Server
```bash
python run.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| JWT_SECRET_KEY | Secret key for JWT tokens | Yes |
| GOOGLE_MAPS_API_KEY | Google Maps API key | No |
| MAIL_USERNAME | SMTP email username | No |
| MAIL_PASSWORD | SMTP email password | No |

## Default Database URL
```
postgresql://postgres:postgres@localhost:5432/deliveroo
```

## Common Issues

### "password authentication failed for user postgres"
Run the setup script or reset your PostgreSQL password:
```bash
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'postgres';
```

### "database does not exist"
Create the database:
```bash
sudo -u postgres createdb deliveroo
```
