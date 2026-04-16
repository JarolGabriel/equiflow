# 🚀 EquiFlow API | Advanced Fintech Portfolio Manager

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

```plaintext
├── apps/
│   ├── alerts/         # Real-time price thresholds & WebSockets
│   ├── investments/    # Core: Portfolios, Transactions & WAC Signals
│   ├── market_data/    # External API integrations & Celery Tasks
│   ├── payments/       # Stripe Integration & Webhooks
│   └── users/          # Custom User Model & JWT/Social Auth
├── core/               # Project settings & ASGI/WSGI config
├── conftest.py         # Global Pytest fixtures
└── pytest.ini          # Testing configuration

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