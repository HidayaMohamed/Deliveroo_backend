# Deliveroo Backend

A RESTful API for a parcel delivery management system built with Flask. Supports customer order placement, real-time courier tracking, admin management, M-Pesa payments, and email notifications.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Orders](#orders)
  - [Courier](#courier)
  - [Admin](#admin)
  - [Payments (M-Pesa)](#payments-m-pesa)
- [Data Models](#data-models)
- [Services](#services)
- [Role-Based Access Control](#role-based-access-control)
- [Order Status Flow](#order-status-flow)

---

## Tech Stack

| Layer          | Technology                                   |
| -------------- | -------------------------------------------- |
| Framework      | Flask, Flask-RESTful                         |
| Database       | PostgreSQL + SQLAlchemy                      |
| Migrations     | Flask-Migrate (Alembic)                      |
| Authentication | Flask-JWT-Extended (access + refresh tokens) |
| Passwords      | Flask-Bcrypt                                 |
| Payments       | Safaricom M-Pesa Daraja API                  |
| Email          | Flask-Mail (Gmail SMTP)                      |
| Maps/Distance  | Google Maps Distance Matrix API              |
| CORS           | Flask-CORS                                   |
| Validation     | Custom validators + phonenumbers             |
| Serialization  | SQLAlchemy-Serializer                        |

---

## Project Structure

```
Deliveroo_backend/
├── app/
│   ├── __init__.py              # App factory, route registration, CORS config
│   ├── models/
│   │   ├── __init__.py          # Model exports
│   │   ├── user.py              # User model (customer, courier, admin)
│   │   ├── courier.py           # Courier profile model
│   │   ├── delivery.py          # DeliveryOrder model, OrderStatus, WeightCategory
│   │   ├── order_tracking.py    # GPS tracking history per order
│   │   ├── payment.py           # Payment model (M-Pesa, card, cash)
│   │   └── notification.py      # In-app notifications
│   ├── routes/
│   │   ├── auth_routes.py       # Register, login, me, refresh token
│   │   ├── order_routes.py      # CRUD orders, tracking, price estimates
│   │   ├── courier_routes.py    # Courier order management & location updates
│   │   ├── admin_routes.py      # Admin dashboard, assign couriers, manage orders
│   │   └── payment_routes.py    # M-Pesa STK push & callbacks
│   ├── services/
│   │   ├── email_service.py     # Email notifications (status, assignment, delivery)
│   │   ├── maps_service.py      # Google Maps distance calculation
│   │   ├── payment_service.py   # M-Pesa Daraja API integration
│   │   └── pricing_service.py   # Delivery price calculation engine
│   ├── utils/
│   │   └── role_guards.py       # Role-based access decorators
│   └── validators/
│       └── order_validators.py  # Order creation & update validation
├── migrations/                  # Alembic migration files
├── app.py                       # Entry point with CLI commands & error handlers
├── run.py                       # Minimal run script
├── config.py                    # App configuration (DB, JWT, Mail, Maps)
├── extensions.py                # SQLAlchemy, Bcrypt, JWT instances
├── seed.py                      # Database seeding (admin, sample users)
├── Pipfile                      # Dependencies
└── .env                         # Environment variables (git-ignored)
```

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Pipenv

### Install dependencies

```bash
pipenv install
pipenv shell
```

---

## Database Setup

```bash
# 1. Create the PostgreSQL database
createdb deliveroo

# 2. Initialize migrations (only once, already done if migrations/ exists)
flask db init

# 3. Generate migration from models
flask db migrate -m "initial models"

# 4. Apply migration to database
flask db upgrade

# 5. Seed with default users (admin, sample courier, sample customer)
python seed.py
```

### Quick Alternative (SQLite, dev only)

If you don't want to install Postgres for quick local testing:

```bash
export DATABASE_URL="sqlite:///dev.db"
python seed.py
```

### Default Seed Users

| Role     | Email                | Password  |
| -------- | -------------------- | --------- |
| Admin    | admin@example.com    | adminpass |
| Courier  | courier@example.com  | password  |
| Customer | customer@example.com | password  |

---

## Environment Variables

Create a `.env` file in the project root (already git-ignored):

```env
# Flask
FLASK_DEBUG=True
PORT=5000

# Database
DATABASE_URL=postgresql:///deliveroo

# JWT
JWT_SECRET_KEY=your-random-secret-key

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Email (Gmail SMTP)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=noreply@deliveroo.com

# M-Pesa Daraja API (sandbox defaults pre-filled)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://your-ngrok-url.ngrok.io/api/payments/callback

# Seed Data
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=adminpass
SAMPLE_PASSWORD=password
```

### Getting API Keys

- **Google Maps**: [Google Cloud Console](https://console.cloud.google.com/) — enable the **Distance Matrix API**
- **M-Pesa Sandbox**: [Safaricom Daraja Portal](https://developer.safaricom.co.ke/) — register and create a sandbox app
- **Gmail App Password**: Enable 2FA on your Google account, then generate an app password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- **JWT Secret**: Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Running the Server

```bash
# Option 1: Full entry point (with CLI commands & startup banner)
python app.py

# Option 2: Minimal run
python run.py

# Option 3: Flask CLI
flask run
```

The API runs on `http://127.0.0.1:5000` by default.

### Available CLI Commands

```bash
flask create-db     # Create all database tables
flask drop-db       # Drop all tables (with confirmation prompt)
flask seed-db       # Seed database with default users
flask db migrate    # Generate a new migration
flask db upgrade    # Apply pending migrations
flask shell         # Open Flask shell with db context
```

---

## API Endpoints

All endpoints are prefixed with `/api`.

### Authentication

| Method | Endpoint             | Auth          | Description                  |
| ------ | -------------------- | ------------- | ---------------------------- |
| POST   | `/api/auth/register` | No            | Register a new user          |
| POST   | `/api/auth/login`    | No            | Login and receive JWT tokens |
| GET    | `/api/auth/me`       | JWT           | Get current user profile     |
| POST   | `/api/auth/refresh`  | Refresh Token | Get new access token         |

#### Register — `POST /api/auth/register`

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "phone": "+254712345678",
  "role": "customer"
}
```

> For couriers, also include `"vehicle_type"` and `"plate_number"` (both required).

#### Login — `POST /api/auth/login`

```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "message": "Login successful",
  "user": { "id": 1, "email": "john@example.com", "role": "customer" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

Use the `access_token` in subsequent requests as:

```
Authorization: Bearer <access_token>
```

---

### Orders

| Method | Endpoint                       | Auth     | Description                         |
| ------ | ------------------------------ | -------- | ----------------------------------- |
| POST   | `/api/orders/`                 | JWT      | Create a new delivery order         |
| GET    | `/api/orders/`                 | JWT      | List orders (filtered by user role) |
| GET    | `/api/orders/<id>`             | JWT      | Get order details                   |
| PATCH  | `/api/orders/<id>/destination` | JWT      | Update destination (pending only)   |
| POST   | `/api/orders/<id>/cancel`      | JWT      | Cancel an order                     |
| GET    | `/api/orders/<id>/tracking`    | JWT      | Get order tracking history          |
| POST   | `/api/orders/estimate`         | Optional | Get price estimate without creating |

#### Create Order — `POST /api/orders/`

```json
{
  "pickup_lat": -1.2921,
  "pickup_lng": 36.8219,
  "pickup_address": "Nairobi CBD, Kenyatta Avenue",
  "pickup_phone": "+254712345678",
  "destination_lat": -1.3028,
  "destination_lng": 36.7073,
  "destination_address": "Westlands, Sarit Centre",
  "destination_phone": "+254798765432",
  "weight_kg": 5.5,
  "parcel_description": "Electronics package",
  "parcel_dimensions": "30x20x15",
  "fragile": true,
  "insurance_required": false,
  "is_express": false,
  "is_weekend": false
}
```

**Response includes:** order details, tracking number, pricing breakdown, and estimated delivery time.

#### Price Estimate — `POST /api/orders/estimate`

```json
{
  "pickup_lat": -1.2921,
  "pickup_lng": 36.8219,
  "destination_lat": -4.0435,
  "destination_lng": 39.6682,
  "weight_kg": 10,
  "is_express": true
}
```

---

### Courier

All courier endpoints require JWT with `courier` role.

| Method | Endpoint                            | Description                      |
| ------ | ----------------------------------- | -------------------------------- |
| GET    | `/api/courier/orders`               | List assigned orders             |
| GET    | `/api/courier/orders/<id>`          | Get assigned order details       |
| PATCH  | `/api/courier/orders/<id>/status`   | Update order status              |
| PATCH  | `/api/courier/orders/<id>/location` | Update current GPS location      |
| GET    | `/api/courier/stats`                | Get personal delivery statistics |

#### Update Status — `PATCH /api/courier/orders/<id>/status`

```json
{
  "status": "PICKED_UP",
  "notes": "Picked up from reception"
}
```

> Valid courier transitions: `ASSIGNED` -> `PICKED_UP` -> `IN_TRANSIT` -> `DELIVERED`

#### Update Location — `PATCH /api/courier/orders/<id>/location`

```json
{
  "latitude": -1.2855,
  "longitude": 36.8263,
  "location_description": "Along Uhuru Highway"
}
```

---

### Admin

All admin endpoints require JWT with `admin` role.

| Method | Endpoint                        | Description                    |
| ------ | ------------------------------- | ------------------------------ |
| GET    | `/api/admin/users`              | List all users                 |
| GET    | `/api/admin/orders`             | List all orders (with filters) |
| PATCH  | `/api/admin/orders/<id>/assign` | Assign courier to order        |
| PATCH  | `/api/admin/orders/<id>/status` | Override order status          |
| GET    | `/api/admin/stats`              | Dashboard statistics           |

#### Assign Courier — `PATCH /api/admin/orders/<id>/assign`

```json
{
  "courier_id": 2
}
```

#### Admin Stats — `GET /api/admin/stats?period=today`

Query params: `period` = `today` | `week` | `month` | `all`

**Response:**

```json
{
  "period": "today",
  "summary": {
    "total_orders": 45,
    "total_revenue": 125000.0,
    "active_couriers": 8,
    "couriers_on_delivery": 5,
    "average_delivery_time_minutes": 42.5
  },
  "orders_by_status": {
    "pending": 5,
    "assigned": 3,
    "picked_up": 2,
    "in_transit": 4,
    "delivered": 28,
    "cancelled": 3
  },
  "recent_orders": []
}
```

#### Filter Orders — `GET /api/admin/orders`

Query params: `status`, `courier_id`, `date_from`, `date_to`, `limit`, `page`

```
GET /api/admin/orders?status=PENDING&date_from=2026-01-01&limit=10&page=1
```

---

### Payments (M-Pesa)

| Method | Endpoint                                    | Description                            |
| ------ | ------------------------------------------- | -------------------------------------- |
| POST   | `/api/payments/initiate`                    | Initiate M-Pesa STK Push               |
| POST   | `/api/payments/callback`                    | M-Pesa callback (Safaricom calls this) |
| GET    | `/api/payments/status/<order_id>`           | Get payment status for an order        |
| GET    | `/api/payments/query/<checkout_request_id>` | Query M-Pesa transaction status        |
| POST   | `/api/payments/orders/<order_id>/pay`       | Pay for order (alias for initiate)     |
| POST   | `/api/payments/test`                        | Test STK Push (dev only)               |

#### Initiate Payment — `POST /api/payments/initiate`

```json
{
  "order_id": 1,
  "phone_number": "0712345678"
}
```

**Response:**

```json
{
  "success": true,
  "message": "STK push sent. Check your phone to complete payment.",
  "payment_id": 1,
  "transaction_reference": "PAY250210143012",
  "checkout_request_id": "ws_CO_...",
  "amount": 850.0,
  "currency": "KES"
}
```

#### Testing M-Pesa Locally

1. Install [ngrok](https://ngrok.com/) and start a tunnel: `ngrok http 5000`
2. Set `MPESA_CALLBACK_URL` in `.env` to the ngrok HTTPS URL + `/api/payments/callback`
3. Use the test endpoint: `POST /api/payments/test` with a Safaricom sandbox phone number

---

## Data Models

### User

Supports three roles: `customer`, `courier`, `admin`. Couriers require `vehicle_type` and `plate_number` (enforced by a database check constraint). Passwords are hashed with bcrypt. Phone numbers are validated using the `phonenumbers` library and must include a country code.

### DeliveryOrder

Central model with pickup/destination coordinates, parcel details (weight, dimensions, fragile flag), full pricing breakdown, status tracking, and relationships to payment, tracking updates, and notifications.

### CourierProfile

Extended profile for couriers with vehicle info, verification status, total delivery count, and rating.

### Payment

Tracks M-Pesa and card payments with transaction references, M-Pesa receipt numbers, checkout/merchant request IDs, and status lifecycle (PENDING -> PROCESSING -> PAID / FAILED / REFUNDED / CANCELLED).

### OrderTracking

GPS location history for each order. Records latitude, longitude, status at time of update, courier speed, device battery level, GPS accuracy, and optional photo proof URL.

### Notification

In-app notifications for users about order updates, courier assignments, and status changes. Tracks read/unread state.

---

## Services

### PricingService

Calculates delivery prices based on:

- **Base fare**: KES 150
- **Distance rate**: KES 50/km (distance from Google Maps Distance Matrix API)
- **Weight tiers**: Small (<5kg: KES 150), Medium (5-20kg: KES 300), Large (20-50kg: KES 500), XLarge (>50kg: KES 1000)
- **Surcharges**: Fragile (+15%), Insurance (+10%), Express (+25%), Weekend (+20%)
- **Estimated delivery time**: Based on 40 km/h normal, 60 km/h express + handling buffer

### MapsService

Wraps the Google Maps Distance Matrix API to calculate driving distance (km) and duration (minutes) between pickup and destination coordinates.

### MpesaService (Payment Service)

Full Safaricom M-Pesa Daraja API integration:

- OAuth access token generation
- STK Push (Lipa Na M-Pesa Online) initiation
- Callback parsing for payment confirmation
- Transaction status queries
- Phone number formatting (handles `0712...`, `+254712...`, `254712...`)
- Supports sandbox and production environments

### EmailService

Sends transactional emails via Gmail SMTP:

- **Status updates** — when order status changes
- **Courier assigned** — when admin assigns a courier to an order
- **Delivery complete** — when order is marked as delivered

---

## Role-Based Access Control

Access is enforced via JWT claims and decorator guards defined in `app/utils/role_guards.py`:

| Decorator                 | Allowed Roles  | Used In         |
| ------------------------- | -------------- | --------------- |
| `@admin_required`         | admin          | Admin routes    |
| `@courier_required`       | courier        | Courier routes  |
| `@customer_required`      | customer       | Customer routes |
| `@admin_courier_required` | admin, courier | Shared routes   |

The user's role is automatically embedded in the JWT token via the `additional_claims_loader` in `extensions.py`. The decorators verify the claim on each request.

---

## Order Status Flow

```
PENDING ──> ASSIGNED ──> PICKED_UP ──> IN_TRANSIT ──> DELIVERED
   |            |            |
   v            v            v
CANCELLED   CANCELLED   CANCELLED
```

| Status     | Description                        | Who Can Set It       |
| ---------- | ---------------------------------- | -------------------- |
| PENDING    | Order created, awaiting courier    | System (on creation) |
| ASSIGNED   | Admin assigned a courier           | Admin                |
| PICKED_UP  | Courier picked up the parcel       | Courier              |
| IN_TRANSIT | Courier is en route to destination | Courier              |
| DELIVERED  | Parcel delivered successfully      | Courier              |
| CANCELLED  | Order cancelled                    | Customer, Admin      |

---

## License

This project is part of a Phase 5 capstone project.
