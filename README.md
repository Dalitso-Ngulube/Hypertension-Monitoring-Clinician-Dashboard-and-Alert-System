# Hypertension Monitoring Clinician Dashboard & Alert System

> A full‑stack web application that helps clinicians to monitor hypertensive patients, analyse blood pressure trends, classify risk according to AHA/ACC guidelines, and receive real‑time alerts for critical readings.

---

## Table of Contents

- [Hypertension Monitoring Clinician Dashboard \& Alert System](#hypertension-monitoring-clinician-dashboard--alert-system)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [System Architecture](#system-architecture)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Backend Setup](#backend-setup)
      - [1. Clone the Repository](#1-clone-the-repository)

---

## Overview

Hypertension is a leading global health challenge, particularly in resource‑constrained regions. This project addresses the gap between patient‑generated blood pressure data and effective clinical management. It provides a **secure, web‑based dashboard** for clinicians to:

- View patient profiles and medical histories.
- Track BP trends over time (7/30/90 days).
- Classify risk automatically using  guidelines.
- Receive real‑time alerts for critical readings.
- Access clinical decision support (medication recommendations, lab suggestions).
- Manage appointments and export reports (CSV).

The system is built with a **React frontend**, **Django REST API**, and **PostgreSQL** database, with role‑based access for Admin, Clinician, and Patient.

---

##  Features

- **Patient Management** – Full CRUD with detailed medical history (comorbidities, lifestyle, allergies, medications, BMI).
- **BP Data Collection** – Manual entry via API; extensible for future device integration.
- **Automated Risk Classification** – Implements AHA/ACC thresholds (Normal, Elevated, Stage 1, Stage 2, Crisis).
- **Interactive Dashboard** – Real‑time stats, trend charts, and time‑of‑day pattern analysis.
- **Real‑Time Alerts** – Auto‑generated for crisis/stage‑2 readings; clinicians can resolve alerts.
- **Clinical Decision Support** – Stage‑based medication recommendations, lab investigations, and lifestyle modifications.
- **Appointment Scheduling** – Manage appointments with status tracking (Scheduled/Completed/Cancelled).
- **Role‑Based Access** – Distinct views for Admin, Clinician, and Patient.
- **Dark Mode** – Toggle for comfortable viewing.
- **CSV Export** – Download patient data and summary reports.
- **Auto‑Logout** – Idle session timeout (15 minutes) for security.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Bootstrap 5, Custom CSS, Vite |
| **Backend** | Django 5.1, Django REST Framework, SimpleJWT |
| **Database** | PostgreSQL 15 |
| **APIs** | RESTful (JSON) |
| **Charts** | Chart.js / React‑Chartjs‑2 |
| **Icons** | Lucide React |
| **Authentication** | JWT (JSON Web Tokens) |
| **Notifications** | Email (Django console in dev), SMS via Twilio (planned) |
| **Version Control** | Git & GitHub |

---

## System Architecture

The system follows a **3‑tier architecture**:

1. **Frontend (React)** – Renders the dashboard, charts, and alerts; communicates with the backend via REST APIs.
2. **Backend (Django)** – Handles business logic, authentication, risk classification, alert generation, and data persistence.
3. **Database (PostgreSQL)** – Stores patient records, BP readings, alerts, appointments, and user data.

All communication is secured with **JWT tokens** and **HTTPS** (in production).

---

## Getting Started

Follow these steps to set up the project locally for development and testing.

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **PostgreSQL 14+**
- **Git**

---

### Backend Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Hypertension-Monitoring-Clinician-Dashboard-and-Alert-System.git
cd Hypertension-Monitoring-Clinician-Dashboard-and-Alert-System
2. Create and Activate a Virtual Environment
bash
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
3. Install Python Dependencies
bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the project root (next to manage.py) with the following content:

env
SECRET_KEY=your_super_strong_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=hypertension_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
Generate a secure SECRET_KEY using:

bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
5. Create the Database
sql
-- In PostgreSQL shell or pgAdmin
CREATE DATABASE hypertension_db;
6. Run Migrations
bash
python manage.py makemigrations
python manage.py migrate
7. Create a Superuser (Admin)
bash
python manage.py createsuperuser
8. Seed Reference Data (Optional)
bash
python manage.py seed_medical_data
9. Seed Simulated Patients (Optional)
bash
python manage.py seed   # or your custom seed script
10. Start the Django Development Server
bash
python manage.py runserver
The backend API will be available at http://localhost:8000.

Frontend Setup

1. Navigate to the Frontend Directory
bash
cd frontend

2. Install Dependencies
bash
npm install

3. Set Frontend Environment Variables
Create a .env file in the frontend folder:
env
VITE_API_BASE_URL=http://localhost:8000/api

4. Start the React Development Server
bash
npm run dev
The frontend will be available at http://localhost:3000.

 Running the Application
Backend: http://localhost:8000

Frontend: http://localhost:3000

Django Admin: http://localhost:8000/admin (use the superuser credentials)

The frontend communicates with the backend via the API base URL defined in the environment.

 API Overview (Key Endpoints)
Endpoint	Method	Description
/api/auth/login/	POST	JWT login (returns access & refresh tokens)
/api/auth/me/	GET	Get current user details
/api/patients/	GET/POST	List or create patients (role‑filtered)
/api/bp_readings/	GET/POST	BP readings (role‑filtered)
/api/alerts/unresolved/	GET	Unresolved alerts for the clinician
/api/analytics/summary/	GET	Dashboard stats (patients, readings, alerts, crisis)
/api/analytics/trends/<id>/	GET	Daily aggregated BP trend data for a patient
/api/appointments/appointments/	GET/POST	Manage appointments
/api/analytics/export/patient/<id>/	GET	Export patient data as CSV


Testing
Backend Tests
bash
python manage.py test
a
 Security
The system implements several security measures:

Authentication: JWT with short‑lived access tokens and refresh tokens.

Authorisation: Role‑based access (Admin, Clinician, Patient) enforced at the API level.

Password Hashing: PBKDF2 (Django default).

Input Validation: DRF serializers and model validators.

CORS: Restricted to trusted origins in production.

Auto‑Logout: Frontend idle timeout (15 minutes).

Note: This project is in active development. A full security audit and hardening will be completed before production deployment. 
 Project Structure (Simplified)
text
.
├── backend/
│   ├── accounts/          # Custom user model & authentication
│   ├── patients/          # Patient management & medical history
│   ├── bp_readings/       # BP data & risk classification
│   ├── alerts/            # Alert generation & resolution
│   ├── analytics/         # Dashboards, trends, CDS, risk assessment
│   ├── appointments/      # Appointment scheduling
│   ├── notifications/     # Email/SMS infrastructure
│   └── core/              # Shared utilities & base models
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios configuration
│   │   ├── components/    # Reusable UI components
│   │   ├── context/       # Auth & Theme providers
│   │   ├── pages/         # Route‑level components
│   │   ├── hooks/         # Custom hooks (useIdleTimeout)
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── .env
├── .gitignore
├── SECURITY.md
└── README.md
