# API Usage Guide

This project exposes an OpenAPI/Swagger API for the logistics backend. The API is designed for the real operating model of the platform: sellers receive multiple orders, buyers place orders across multiple sellers, and admins monitor operational exceptions and analytics.

## 1. Start the API server

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 2. API documentation access

FastAPI automatically generates interactive API docs from the route definitions and Pydantic schemas.

Use the Swagger UI when you want to:

- inspect endpoints
- submit live requests
- test authentication flows
- review expected request/response formats

Use the OpenAPI JSON when you want:

- API contract generation
- client SDK generation
- CI validation for API changes
- automation and integration testing

## 3. Authentication and roles

The platform supports role-based access for buyers, sellers, and admins.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json
```

Request body:

```json
{
  "email": "buyer@demo.local",
  "role": "buyer"
}
```

Response:

```json
{
  "token": "<jwt-token>",
  "user": {
    "id": 1,
    "email": "buyer@demo.local",
    "role": "buyer"
  }
}
```

Use the returned token in the Authorization header:

```http
Authorization: Bearer <jwt-token>
```

## 4. Common API flows

### 4.1 Create an order

```http
POST /api/v1/orders
Authorization: Bearer <token>
Content-Type: application/json
```

Example body:

```json
{
  "buyer_id": 1,
  "seller_id": 2,
  "requested_slot": "18:30",
  "items": [
    {
      "menu_item_id": 101,
      "quantity": 2,
      "unit_price": 120.0
    }
  ]
}
```

### 4.2 List orders

```http
GET /api/v1/orders
Authorization: Bearer <token>
```

### 4.3 Update order status

```http
PATCH /api/v1/orders/1/status
Authorization: Bearer <token>
Content-Type: application/json
```

Example body:

```json
{
  "status": "accepted",
  "reason": "seller_confirmed"
}
```

### 4.4 Create a batch

```http
POST /api/v1/batches?seller_id=2
Authorization: Bearer <token>
```

### 4.5 Verify pickup

```http
POST /api/v1/pickups/verify?order_id=1&buyer_id=1
Authorization: Bearer <token>
```

### 4.6 Admin exception creation

```http
POST /api/v1/admin/exceptions
Authorization: Bearer <token>
Content-Type: application/json
```

Example body:

```json
{
  "order_id": 1,
  "exception_type": "delay",
  "severity": "medium",
  "reason": "seller prep exceeded expected window"
}
```

### 4.7 Analytics dashboard

```http
GET /api/v1/analytics/dashboard
Authorization: Bearer <token>
```

Returns a dashboard-friendly overview including:

- platform overview
- seller summaries
- active orders
- open exception counts
- queue health signals

## 5. Role permissions

### Buyer

- create orders
- view own order history
- verify pickup for own orders

### Seller

- create batches
- update order status
- review seller queue and seller analytics

### Admin

- create exceptions
- review dashboard metrics
- approve operational actions (no-show, refund, escalations)

## 6. Required response patterns

Most responses are JSON objects with either:

- successful data payloads
- or standard FastAPI error payloads such as:

```json
{
  "detail": "Order not found"
}
```

Typical successful codes:

- 200 OK
- 201 Created
- 202 Accepted (where used)

Typical errors:

- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict

## 7. Example complete flow

```bash
# 1) login as buyer
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@demo.local","role":"buyer"}'

# 2) copy token
# 3) create an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_id": 1,
    "seller_id": 2,
    "requested_slot": "18:30",
    "items": [{"menu_item_id": 101, "quantity": 2, "unit_price": 120.0}]
  }'

# 4) view dashboard analytics
curl -X GET http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer <token>"
```

## 8. Notes

- The app is a demonstration logistics service foundation and can be extended with real auth providers, event streaming, and persistent PostgreSQL migration behavior.
- The OpenAPI docs are the canonical source of truth for the API contract while the service is running.
- For production usage, replace the demo auth flow with real JWT identity providers and secure role policies.
