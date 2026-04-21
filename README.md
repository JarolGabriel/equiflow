# 🚀 EquiFlow API | Advanced Fintech Portfolio Manager

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-orange?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-red?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

EquiFlow is a high-performance financial management API designed to track multi-asset investments (Stocks, Crypto, Forex) in real-time. It features professional-grade architecture including asynchronous tasks, weighted average cost calculations, and automated financial reporting.

---

## 🔗 Quick Links
* **🌐 Live Demo:** [View Live Site](https://equiflow-web.onrender.com/api/redoc/)
* **📖 API Documentation:** [Swagger UI Docs](https://equiflow-web.onrender.com/api/docs/)
* **📁 Repository:** [GitHub Repo](https://github.com/JarolGabriel/equiflow)

> **⚠️ Note on Performance:** This demo is hosted on Render's Free Tier. If the service is idle, the initial request may take **2 to 6 minutes** to spin up the container.

---

## 🛠️ Tech Stack & Cloud Infrastructure
EquiFlow has evolved from a local **Docker-based** setup to a robust **Cloud-Native Architecture**, leveraging managed services for enterprise-grade reliability:

* **Backend:** Django 5.0 & Django Rest Framework (DRF).
* **Database:** **PostgreSQL 16 (via Supabase)**.
* **Caching & Real-time:** **Redis (via Upstash)** powering Django Channels & Celery.
* **Async Processing:** **Celery & Celery Beat** for background price updates.
* **Payments:** **Stripe API** with production Webhook integration.
* **Auth:** JWT (SimpleJWT) + Social Auth (Google/GitHub).
* **Infrastructure:** Deployment via **Render** with automated CI/CD.

---

## 🌟 Key Business Logic (Senior Features)

### 📈 Smart Weighted Average Price (WAC)
Implemented via **Django Signals**. The system automatically recalculates the average purchase price and total quantity every time a `BUY` or `SELL` transaction is recorded, ensuring 100% accurate Profit & Loss (P&L) tracking.

### 🛡️ Subscription & Limits Logic
Custom permission layers enforce business rules based on the user's plan:
* **Portfolios:** 🆓 Free: Max 3 | 💎 **Pro: Unlimited**.
* **Price Alerts:** Real-time monitoring via **WebSockets (Django Channels)**.
* **Financial Reports:** Automated PDF generation via **ReportLab**.
* **Payments:** Automated "Pro" status activation via **Stripe Webhooks**.

### ⏱️ Automated Market Updates
Using **Celery Beat**, the system performs background polling of financial data (via yfinance/AlphaVantage) to keep portfolio valuations updated without user intervention.

---

## 📂 Project Structure


---

## 🛠️ Local Development Setup

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (recommended)
- **PostgreSQL 16** (if not using Docker)
- **Redis** (if not using Docker)

### Installation Steps

1. **Clone the repository**
```bash
   git clone https://github.com/JarolGabriel/equiflow.git
   cd equiflow
```

2. **Create virtual environment** (optional if using Docker)
```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(50))")
   # - Database credentials
   # - STRIPE_SECRET_KEY, ALPHA_VANTAGE_API_KEY, etc.
```

5. **Run with Docker Compose** (recommended)
```bash
   docker-compose up --build
```

6. **Run migrations**
```bash
   # If using Docker:
   docker exec -it equiflow_web python manage.py migrate

   # If running locally:
   python manage.py migrate
```

7. **Create superuser** (optional)
```bash
   # If using Docker:
   docker exec -it equiflow_web python manage.py createsuperuser

   # If running locally:
   python manage.py createsuperuser
```

8. **Access the application**
   - **Swagger UI:** http://localhost:8000/api/docs/
   - **ReDoc:** http://localhost:8000/api/redoc/
   - **Admin Panel:** http://localhost:8000/admin/

### Running Tests
```bash
# If using Docker:
docker exec -it equiflow_web python -m pytest

# If running locally:
python -m pytest
```

---

 
    ├── apps/
    │   ├── alerts/         # Real-time price thresholds & WebSockets
    │   ├── investments/    # Core: Portfolios, Transactions & WAC Signals
    │   ├── market_data/    # External API integrations & Celery Tasks
    │   ├── payments/       # Stripe Integration & Webhooks
    │   └── users/          # Custom User Model & JWT/Social Auth
    ├── core/               # Project settings & ASGI/WSGI config
    ├── conftest.py         # Global Pytest fixtures
    └── pytest.ini          # Testing configuration



---

🧪 Testing & Quality Assurance
We maintain code reliability using Pytest.

Unit Tests: Financial formulas and model methods.

Integration Tests: Signal execution and database consistency.

Security Tests: Data isolation and multi-tenancy verification.

# Run the test suite
python -m pytest

## 🛣️ API Main Endpoints Summary

| Method |         Endpoint                               |     Description |
| :---   |            :---                                |     :---        |
| `GET`  | `/api/investments/assets/`                     | List all available financial assets |
| `POST` | `/api/investments/portfolios/`                 | Create a new investment portfolio |
| `GET`  | `/api/investments/portfolios/{id}/export-pdf/` | Export pro financial report |
| `POST` | `/api/payments/webhook/`                       | Secure Stripe event listener |
| `GET`  | `/api/users/github/login/`                     | Social authentication entry point |


---

# 🔑 Authentication & User Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/register/` | POST | Register a new user account. |
| `/api/users/login/` | POST | Authenticate user and obtain Access/Refresh tokens. |
| `/api/users/password/reset/` | POST | Request a password reset link via email. |
| `/api/users/password/reset/confirm/` | POST | Confirm password reset using the token provided in email. |
| `/api/users/password/change/` | POST | Change password for the authenticated user. |

## Request Body Examples

### User Registration

```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!"
}
```

### Password Reset Confirmation

```json
{
    "uid": "MTI",
    "token": "asdf-1234567890",
    "new_password1": "NewStrongPassword2026!",
    "new_password2": "NewStrongPassword2026!"
}
```

---

# 📈 Investments & Portfolios

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/investments/portfolios/` | GET/POST | List all user portfolios or create a new one. |
| `/api/investments/transactions/` | POST | Record a new BUY or SELL transaction. |
| `/api/investments/assets/` | GET | Get the global catalog of supported assets. |
| `/api/investments/assets/my-favorites/` | GET | Retrieve the user's Watchlist (Favorite assets). |

## Request Body Examples

### Create a Portfolio

```json
{
    "name": "Main Growth Portfolio",
    "description": "Long-term focus on Crypto and Tech stocks",
    "currency": "USD",
    "is_public": false
}
```

### Register a Transaction

**Note:** Transactions automatically update the portfolio's balance and Average Purchase Price (WAC) via Django Signals.

```json
{
    "portfolio": "UUID-OF-YOUR-PORTFOLIO",
    "asset": "UUID-OF-THE-ASSET",
    "transaction_type": "BUY",
    "quantity": 1.25,
    "price_at_transaction": 65400.50
}
```

---

# 🌍 Real-Time Market Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/market/status/` | GET | Fetch live market prices and 24h changes from Redis cache. |

## Sample Response (200 OK)

```json
{
  "status": "success",
  "last_update": "2026-04-16T02:01:53Z",
  "data": {
    "BTC": { 
        "price": 74624.0, 
        "change": 2.5 
    },
    "AAPL": { 
        "price": 266.42, 
        "change": null 
    }
  }
}
```