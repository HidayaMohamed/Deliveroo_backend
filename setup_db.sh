#!/bin/bash

# Deliveroo Database Setup Script
# Run this to configure PostgreSQL for the Deliveroo backend

echo "Setting up PostgreSQL for Deliveroo..."

# Set password for deliveroo_user
echo "Setting password for deliveroo_user..."
sudo -u postgres psql -c "ALTER USER deliveroo_user WITH PASSWORD '123885490';"

# Configure pg_hba.conf for md5 authentication
echo "Configuring pg_hba.conf for password authentication..."
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/12/main/pg_hba.conf

# Restart PostgreSQL
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

echo "Database setup complete!"
echo ""
echo "Now run: flask run"
