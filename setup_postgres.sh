#!/bin/bash

# Deliveroo PostgreSQL Setup Script
# Run this script to configure PostgreSQL for Deliveroo

echo "🐙 Deliveroo PostgreSQL Setup"
echo "=============================="

# Set PostgreSQL password
echo ""
echo "Setting PostgreSQL password to 'postgres'..."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Password set successfully!"
else
    echo "⚠️  Could not set password automatically. Trying alternative method..."
    
    # Alternative: Create a .pgpass file
    echo "localhost:5432:*:postgres:postgres" > ~/.pgpass
    chmod 600 ~/.pgpass
    
    # Try using psql with .pgpass
    psql -h localhost -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Password set via .pgpass!"
    else
        echo "❌ Could not set password. Please run manually:"
        echo "   sudo -u postgres psql"
        echo "   Then run: ALTER USER postgres WITH PASSWORD 'postgres';"
    fi
fi

# Create database
echo ""
echo "Creating 'deliveroo' database..."
sudo -u postgres createdb deliveroo 2>/dev/null || echo "⚠️  Database may already exist or could not be created"

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Deliveroo Environment Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deliveroo
JWT_SECRET_KEY=deliveroo-secret-key-change-in-production
EOF
    echo "✅ .env file created!"
else
    echo "⚠️  .env file already exists. Make sure it has:"
    echo "   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deliveroo"
fi

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: flask db upgrade"
echo "2. Run: python run.py"
echo ""
