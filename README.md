# Inventory API

A small e-commerce **Order & Inventory** backend built with **Django 5** and
**Django REST Framework**, backed by **PostgreSQL**. It exposes a REST API for
managing products and orders.

## Features

- Product catalogue with SKU, stock level and price.
- Orders made up of one or more order items, with a lifecycle status
  (`PENDING`, `CONFIRMED`, `SHIPPED`, `CANCELLED`).
- Order creation that validates availability and adjusts stock.
- Order listing with optional filters by status and creation date.
- Order cancellation and shipping endpoints.
- DRF pagination (10 records per page) and a browsable API.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — the whole
  stack (Django, PostgreSQL, pgAdmin, k6) runs in containers.
- *Optional:* Python 3.10+ and PostgreSQL 12+, if you prefer to run it without
  Docker.

## Quick start with Docker

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test -v 2
```

The API is then at <http://localhost:8000/api/> and pgAdmin at
<http://localhost:5050> (log in with `admin@example.com` / `devpassword`, then
add a server with host `db`, port `5432`, database `inventory_db`).

A step-by-step guide, including a beginner-friendly walkthrough of Docker and
the full recording workflow, is in
[`docs/Debug_and_Refactor_Plan.docx`](docs/Debug_and_Refactor_Plan.docx).

## Manual setup (without Docker)

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the PostgreSQL database:

   ```bash
   createdb inventory_db
   ```

4. Configure the connection using environment variables (all optional, shown
   with their defaults):

   | Variable             | Default                                        |
   | -------------------- | ---------------------------------------------- |
   | `DB_NAME`            | `inventory_db`                                 |
   | `DB_USER`            | `$USER` (falls back to `postgres`)             |
   | `DB_PASSWORD`        | *(empty)*                                      |
   | `DB_HOST`            | `localhost`                                    |
   | `DB_PORT`            | `5432`                                         |
   | `DJANGO_SECRET_KEY`  | development key                                |
   | `DJANGO_DEBUG`       | `True`                                         |
   | `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1`                        |

5. Apply the migrations and create an admin user:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

## API

The API is mounted under `/api/`.

| Method   | Endpoint                        | Description                              |
| -------- | ------------------------------- | ---------------------------------------- |
| `GET`    | `/api/products/`                | List products (paginated).               |
| `POST`   | `/api/products/`                | Create a product.                        |
| `GET`    | `/api/products/{id}/`           | Retrieve a product.                      |
| `PUT/PATCH` | `/api/products/{id}/`        | Update a product.                        |
| `DELETE` | `/api/products/{id}/`           | Delete a product.                        |
| `GET`    | `/api/orders/`                  | List orders (paginated).                 |
| `POST`   | `/api/orders/`                  | Create an order.                         |
| `GET`    | `/api/orders/{id}/`             | Retrieve an order.                       |
| `POST`   | `/api/orders/{id}/cancel/`      | Cancel an order.                         |
| `POST`   | `/api/orders/{id}/ship/`        | Mark an order as shipped.                |

`GET /api/orders/` accepts the following query parameters:

- `status` — exact order status, e.g. `?status=SHIPPED`.
- `start_date` — inclusive lower bound on `created_at`, e.g. `?start_date=2026-01-01`.
- `end_date` — inclusive upper bound on `created_at`, e.g. `?end_date=2026-01-31`.
- `page` — page number, e.g. `?page=2`.

Creating an order:

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2, "customer_email": "shopper@example.com"}'
```

## Tests

```bash
# in Docker
docker compose exec web python manage.py test -v 2

# or, with a local virtual environment
python manage.py test -v 2
```

`scripts/verify.sh` runs the checks, the migration drift check and the suite,
preferring the running `web` container and falling back to a local virtualenv.

## Project layout

```
inventory_api/
├── manage.py
├── requirements.txt
├── Dockerfile           # builds the Django web container
├── docker-compose.yml   # db + web + pgadmin (+ k6 under the "loadtest" profile)
├── .dockerignore
├── .env.example         # template for local database/Django env vars
├── core/                # project package (settings, urls, wsgi/asgi)
├── orders/              # products, orders and order items
├── loadtest/            # k6 checkout.js
├── docs/                # Debug_and_Refactor_Plan.docx
└── scripts/             # verify.sh
```
