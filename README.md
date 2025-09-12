
---
# 🛡️ Coreshield — Risk-Based Passwordless Authentication

> Frictionless. Adaptive. Continuous. Secure.

Coreshield is a next-gen authentication system that eliminates passwords and replaces static MFA with intelligent, risk-based verification. Built for modern apps that demand both security and seamless UX.

---

## 👥 Team Members

| Role               | Name                     | Responsibilities                          |
|--------------------|--------------------------|-------------------------------------------|
| Product Designer   | Emmanuel Ayobami         | User flows, microcopy, UX prototypes      |
| Frontend Engineer  | Ajose Samuel             | React + Web Crypto: passwordless, device binding, signals |
| Backend Engineer   | Ajayi Oluwatosin J.      | FastAPI + Postgres + Risk Engine + Adaptive MFA |
| AI/ML Engineer     | Sunday Aspita Abraham    | Risk Scoring ML model: IsolationForest / LOF |

---

## 🎯 The Problem

Passwords are weak, reused, and easily compromised. Traditional MFA (e.g., OTP every login) frustrates users and adds unnecessary friction.

**We need authentication that is:**
- ✅ Secure by design  
- ✅ Frictionless for trusted users  
- ✅ Adaptive to real-time risk  
- ✅ Continuously verified  

---

## ✨ Our Solution

**Coreshield** implements a **risk-based, passwordless authentication system** with continuous verification.

### 🔑 Core Features

- **Passwordless Login**  
  Browser generates public/private keypair (stored securely in IndexedDB).

- **Device-Bound Authentication**  
  Device fingerprint + certificate-style binding ensures only authorized devices can authenticate.

- **🧠 Real-Time Risk Engine**  
  Combines device posture, network signals, and behavioral analytics → outputs dynamic risk score (0–100).

- **🔄 Adaptive MFA**  
  Only prompts for OTP or step-up when risk is medium/high — no unnecessary interruptions.

- **👁️ Continuous Re-Authentication**  
  Active sessions are re-scored in real time; anomalies trigger silent checks or forced re-auth.

- **🔒 Privacy-Preserving**  
  No keylogging. Only metadata collected: timing, RTT, geolocation, device attributes.

- **📊 Full Transparency**  
  Users view login history & trusted devices. Admins monitor live risk events & audit logs.

---

## 🛠 Tech Stack

### Frontend
- React + Vite
- Web Crypto API + IndexedDB
- TailwindCSS
- Framer Motion

### Backend
- FastAPI + Uvicorn
- PostgreSQL (via Supabase)
- Redis (OTP cache + rate limiting)
- PyJWT (RS256 signed tokens)
- SQLModel (ORM)
- Alembic (migrations)

### AI/ML Layer
- scikit-learn (`IsolationForest`, `LocalOutlierFactor`)
- Joblib (model persistence)
- Custom Python feature engineering pipeline

### Infrastructure
- Docker + Docker Compose (local dev)
- Supabase (managed Postgres)
- Render (backend hosting)
- Vercel (frontend hosting)
- mkcert / ngrok (local HTTPS testing)

---

## 📂 Repository Structure

```
coreshield/
├── backend/
│   ├── main.py           # FastAPI app entry
│   ├── models/           # SQLModel schemas
│   ├── routes/           # Auth, device, risk APIs
│   ├── risk_core.py      # Real-time risk scoring logic
│   ├── ml/               # ML model training & inference
│   ├── scripts/          # Seeders, utilities
│   ├── keys/             # RSA JWT signing keys
│   ├── alembic/          # DB migrations
│   ├── .env              # Environment config
│   └── requirements.txt
├── frontend/             # React client
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml    # Local DB/Redis setup
└── README.md
```

---

## 🌐 Live Demo

🔗 **Frontend**: [https://osatcoreshield.vercel.app](https://osatcoreshield.vercel.app)  
🔌 **Backend API**: [https://core-shield.onrender.com/api](https://core-shield.onrender.com/api)  
🎥 **Recorded Walkthrough**: [Loom Demo](https://www.loom.com/share/6b9e37f75f284b20bfe8d47290d6d812)

---

## ⚙️ Local Setup Guide

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/coreshield.git
cd coreshield
```

---

### 2. Generate RSA Keys for JWT

```bash
mkdir -p backend/keys
openssl genrsa -out backend/keys/private.pem 2048
openssl rsa -in backend/keys/private.pem -pubout -out backend/keys/public.pem
```

---

### 3. Configure Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### ➕ Create `.env` file in `backend/`

```env
DATABASE_URL=postgresql://postgres.yourproject:[YOUR_SUPABASE_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
REDIS_URL=redis://:password@your-render-redis-host:6379/0
JWT_PRIVATE_KEY_PATH=keys/private.pem
JWT_PUBLIC_KEY_PATH=keys/public.pem
EMAIL_SMTP=smtp.example.com
EMAIL_USER=demo@example.com
EMAIL_PASS=yourpassword
```

---

### 4. Start Services

#### Option A: Use Docker (Recommended for Dev)

```bash
docker-compose up -d
```
> Postgres: `localhost:5432` | Redis: `localhost:6379`

#### Option B: Use Supabase Directly  
Copy `DATABASE_URL` from Supabase → Settings → Database.

---

### 5. Run Migrations

```bash
alembic upgrade head
```

---

### 6. Train ML Risk Model

```bash
cd backend/ml
python train_model.py
```
> Outputs `ml_model.joblib` used by risk engine.

---

### 7. Seed Demo Accounts

```bash
python scripts/seed_demo.py
```

---

### 8. Launch Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 9. Launch Frontend

```bash
cd ../frontend
npm install
npm run dev
```
> Visit: http://localhost:5173

---

## 🔐 Risk Levels & Security Triggers

| Risk Score | Trigger Examples                          | System Response             | User Experience             | Security Actions               |
|------------|-------------------------------------------|------------------------------|-----------------------------|--------------------------------|
| **0–30**   | Known device, same location, normal typing | Issue 4h JWT                 | Silent login + “Trusted” badge | Standard session               |
| **31–60**  | New Wi-Fi, higher RTT, slight behavior diff | Require OTP + 30m JWT        | Modal OTP prompt            | Step-up auth, enhanced logging |
| **61–100** | New device + foreign IP + erratic behavior  | Block login attempt          | Blocked screen + support CTA | Revoke sessions, admin alert   |

> ⚠️ **Unauthorized attempts** (invalid sig, tampered token, brute force) always trigger **≥ Medium Risk** and enforce step-up or block.

---

## 🚀 Demo Scenarios

Try these in your local or live environment:

1. **✅ Happy Path** — Login from known device & location → instant access.
2. **🟡 Medium Risk** — Switch to hotel Wi-Fi → prompted for OTP.
3. **🔴 High Risk** — New device + suspicious geo → blocked with alert.
4. **🔁 Continuous Auth** — Mid-session anomaly detected → silent challenge or forced re-auth.

---

## 📜 License

MIT © 2025 Coreshield Team  
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies.

---

> 💡 **Tip**: Star this repo if you found it useful! Contributions welcome.
```

--- 
