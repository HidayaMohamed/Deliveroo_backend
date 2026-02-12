#!/bin/bash

# Complete PostgreSQL Setup for Deliveroo
# Run these commands manually in terminal:

# 1. Create the deliveroo_user if it doesn't exist
echo "Creating deliveroo_user role..."
sudo -u postgres createuser -s deliveroo_user

# 2. Set the password
echo "Setting password for deliveroo_user..."
sudo -u postgres psql -c "ALTER USER deliveroo_user WITH PASSWORD '123885490';"

# 3. Create the database
echo "Creating deliveroo_db database..."
sudo -u postgres createdb deliveroo_db

# 4. Grant privileges
echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE deliveroo_db TO deliveroo_user;"

# 5. Configure pg_hba.conf for md5 authentication
echo "Configuring pg_hba.conf..."
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/12/main/pg_hba.conf

# 6. Restart PostgreSQL
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

echo ""
echo "Setup complete! Now run: flask run"
