# Phase 1 Implementation Guide

## 1. Folder Structure

```text
/
├── backend/
│   ├── alembic/              # Alembic database migrations
│   ├── app/
│   │   ├── api/              # API Endpoints (Auth, Users, Health)
│   │   ├── core/             # Security (JWT) and Configuration
│   │   ├── db/               # SQLAlchemy Models (Users, Campaigns, AuditLogs, etc.)
│   │   ├── schemas/          # Pydantic Schemas
│   │   ├── services/         # Palladium API Client & Business Logic
│   │   └── main.py           # FastAPI Entry Point
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/       # Authentication pages (Login)
│   │   │   ├── (dashboard)/  # Protected routes (Dashboard, Layout)
│   │   │   └── layout.tsx    # Root layout
│   │   ├── components/       # Reusable components (Sidebar)
│   │   ├── lib/              # API Client (Axios interceptors)
│   │   └── store/            # Zustand global state (Auth store)
│   ├── package.json          # Node dependencies
│   └── tailwind.config.ts    # Tailwind CSS Configuration
└── README.md                 # Setup & Deployment instructions (This file)
```

---

## 2. Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL Server

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize the database schema with Alembic:
   - Run `alembic init alembic`
   - Configure `alembic.ini` with your `DATABASE_URL`
   - Create the initial migration: `alembic revision --autogenerate -m "Initial schema"`
   - Apply migrations: `alembic upgrade head`
6. Run the development server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

---

## 3. Azure Deployment Instructions (Backend)

1. **Provision Azure Resources:**
   - Create an **Azure Database for PostgreSQL Flexible Server**.
   - Create an **Azure App Service (Linux)**.
   - Create an **Azure Cache for Redis** (if preparing for Celery tasks in Phase 2).
2. **Deploy the Code:**
   - Ensure you have a `requirements.txt` and an `app/main.py` ready.
   - You can deploy directly via VS Code Azure extension or GitHub Actions.
   - Set the startup command in the App Service configuration to: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. **Configure Environment Variables** in the App Service (see Section 5).

---

## 4. Vercel Deployment Instructions (Frontend)

1. Connect your GitHub repository to Vercel.
2. Select the `frontend` folder as the Root Directory during project import.
3. Vercel will automatically detect Next.js and apply the correct build commands (`npm run build`).
4. Set the necessary Environment Variables in the Vercel dashboard.
5. Deploy.

---

## 5. Environment Variables List

### Backend (`backend/.env` or Azure App Service Settings)
- `DATABASE_URL`: Your PostgreSQL connection string (e.g., `postgresql+asyncpg://user:pass@host/dbname`)
- `JWT_SECRET_KEY`: A secure random string for signing JWT tokens.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens (e.g., `11520`).
- `PALLADIUM_API_TOKEN`: The API token provided for the Palladium API.
- `PALLADIUM_API_URL`: `https://api.palladium.expert`

### Frontend (`frontend/.env.local` or Vercel Settings)
- `NEXT_PUBLIC_API_URL`: The URL of your deployed backend API (e.g., `https://my-backend-app.azurewebsites.net/api/v1`). For local development, use `http://localhost:8000/api/v1`.

---

## 6. Local Development Guide

1. **Database:** Ensure you have a local PostgreSQL instance running. Create a database named `palladium`. Update the `DATABASE_URL` in `backend/app/core/config.py` (or `.env` file) to match your local credentials.
2. **Running Backend:** With the virtual environment active, run `uvicorn app.main:app --reload`. The API docs will be available at `http://localhost:8000/api/v1/docs`.
3. **Running Frontend:** Run `npm run dev`. The application will be available at `http://localhost:3000`.
4. **Testing the Flow:**
   - Use the FastAPI `/docs` to create a new user (or manually insert one via SQL).
   - Go to `http://localhost:3000/login` and log in with those credentials.
   - You will be redirected to the Dashboard, validating the JWT authentication flow and protected routes.