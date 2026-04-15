# 🚀 EquiFlow API | Advanced Fintech Portfolio Manager

EquiFlow is a high-performance financial management API designed to track multi-asset investments (Stocks, Crypto, Forex) in real-time. It features professional-grade architecture including asynchronous tasks, weighted average cost calculations, and automated financial reporting.

---

## 🔗 Quick Links
* **🌐 Live Demo:** [View Live Site](https://equiflow-web.onrender.com/api/redoc/)
* **📖 API Documentation:** [Swagger UI Docs](https://equiflow-web.onrender.com/api/docs/)
* **📁 Repository:** [GitHub Repo](https://github.com/JarolGabriel/equiflow)

---

## 📸 Preview
![API Documentation Preview](https://via.placeholder.com/800x400?text=Insert+Swagger+UI+Screenshot+Here)

---

## 🛠️ Tech Stack & Architecture
EquiFlow is built with a **microservices-oriented mindset** using Docker Compose:

* **Backend:** Django 5.0 & Django Rest Framework (DRF).
* **Database:** **PostgreSQL 16** for persistent financial records.
* **Caching & Real-time:** **Redis 7** & Django Channels (WebSockets).
* **Async Processing:** **Celery & Celery Beat** for automated market price updates.
* **Payments:** **Stripe API** integration for PRO subscriptions.
* **Auth:** JWT (SimpleJWT) + Social Auth (Google/GitHub).
* **Email:** Integrated with **Resend API**.

---

## 🌟 Key Business Logic (Senior Features)

### 📈 Smart Weighted Average Price (WAC)
Implemented via **Django Signals**. The system automatically recalculates your average purchase price and total quantity every time a `BUY` or `SELL` transaction is recorded, ensuring 100% accurate Profit & Loss (P&L) tracking.

### 🛡️ Subscription & Limits Logic
Custom permission layers and middlewares enforce business rules based on the user's plan:

* **Portfolios:**
    * 🆓 **Free:** Maximum 3 portfolios.
    * 💎 **Pro:** Unlimited portfolios.
* **Price Alerts:**
    * 🆓 **Free:** Up to 3 active alerts.
    * 💎 **Pro:** Unlimited real-time alerts via WebSockets.
* **Financial Reports:**
    * 🆓 **Free:** 1 PDF download included.
    * 💎 **Pro:** Unlimited professional PDF exports and analytics.
* **Payments:** Fully integrated with **Stripe Checkout** and **Webhooks** for automated "Pro" status activation.

### ⏱️ Automated Market Updates
Using **Celery Beat**, the system performs background polling of financial data (via yfinance/AlphaVantage) to keep your portfolio value updated without user intervention.

---

## 🧪 Testing & Quality Assurance
We maintain code reliability using **Pytest**. Our test suite covers:
* **Unit Tests:** Financial formulas and model methods.
* **Integration Tests:** Signal execution and database consistency.
* **Security Tests:** Data isolation (Ensuring User A cannot see User B's portfolio).

**Run tests in Docker:**
```bash
docker compose exec web python -m pytest


🚀 Installation & Setup
1. Clone the project:
clone git@github.com:JarolGabriel/equiflow.git
cd equiflow

2. Configure Environment Variables:

Create a .env file (see .env.example):
STRIPE_SECRET_KEY=sk_test_...
DB_NAME=equiflow
DB_USER=postgres
RESEND_API_KEY=re_...

3. Launch with Docker Compose:
Bashdocker compose up --build

🔑 External Services ConfigurationTo 
enable all features, you must configure the following: 
 OAuth: Update redirect URIs in Google/GitHub consoles to your production domain.
 Payments: Set up Stripe Webhooks to point to /api/payments/webhook/.
 Emails: Add your verified domain in Resend and update the RESEND_API_KEY.
 
📂 Project StructurePlaintext.

├── apps/
│   ├── alerts/        # Real-time price thresholds & WebSockets
│   ├── investments/   # Core: Portfolios, Transactions & WAC Signals
│   ├── market_data/   # External API integrations & Celery Tasks
│   ├── payments/      # Stripe Integration & Webhooks
│   └── users/         # Custom User Model & JWT/Social Auth
├── core/              # Project settings & ASGI/WSGI config
├── media/             # User uploaded profile pictures
├── conftest.py        # Global Pytest fixtures
├── docker-compose.yml # Container orchestration
└── pytest.ini         # Testing configuration

## 🛣️ API Main Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/investments/assets/` | List all available financial assets |
| `POST` | `/api/investments/portfolios/` | Create a new investment portfolio |
| `GET` | `/api/investments/portfolios/{id}/export-pdf/` | Export pro financial report |
| `POST` | `/api/payments/create-intent/` | Handle Stripe subscriptions |
| `GET` | `/api/market/status/` | Get real-time global market status |



```