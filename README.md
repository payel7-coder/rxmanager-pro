# RxManager Pro — Doctor Prescription Management System

A production-level prescription management system built with **Django REST Framework** (backend) and **Vue.js 3** (frontend). Designed for solo-practice and clinic doctors to manage patients, create prescriptions, build reusable templates by disease, and print professional prescriptions.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏥 **Doctor Profile** | Clinic header info printed on every prescription |
| 👤 **Patient Registration** | Auto-generated Patient IDs (PT00001), full medical history |
| 📋 **Prescription Creation** | Vitals, diagnosis, multi-medicine Rx with inline autocomplete |
| 🗂️ **Template System** | Save any prescription as a reusable disease template |
| ✏️ **Template Loading** | Load template → edit freely → original template unchanged |
| 🖨️ **Professional Print** | Branded prescription prints in a new window |
| 📜 **Patient History** | Full Rx history per patient with quick reprint |
| 📊 **Dashboard** | Live stats: today's Rx, month total, recent activity |
| 💊 **Medicine Database** | Searchable medicine list with autocomplete in Rx form |

---

## 🛠 Tech Stack

```
Backend  : Django 4.x + Django REST Framework + django-cors-headers
Database : SQLite (zero-config, swap to PostgreSQL for production)
Frontend : Vue.js 3 (CDN, no build step required)
Fonts    : IBM Plex Sans + Merriweather (Google Fonts)
Icons    : Font Awesome 6
Print    : Native browser print via popup window
```

---

## 🚀 Quick Start

### 1. Install Python dependencies
```bash
pip install django djangorestframework django-cors-headers Pillow reportlab
```

### 2. Start both servers (one command)
```bash
cd rx-manager
bash start.sh
```

This starts:
- Django API → `http://localhost:8000/api/`
- Vue.js Frontend → `http://localhost:5500/`

### 3. Open the app
```
http://localhost:5500
```

---

## 🗂️ Project Structure

```
rx-manager/
├── backend/                    # Django project
│   ├── core/
│   │   ├── models.py           # All data models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API ViewSets
│   │   ├── urls.py             # API routing
│   │   └── admin.py            # Django admin
│   ├── rxmanager/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── db.sqlite3              # Database (auto-created)
│   ├── seed_data.py            # Sample data loader
│   └── manage.py
├── frontend/
│   └── index.html              # Full Vue.js SPA (single file)
├── start.sh                    # One-command launcher
└── README.md
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/` | Stats + recent activity |
| CRUD | `/api/doctors/` | Doctor profile |
| GET | `/api/doctors/primary/` | Fetch first doctor |
| CRUD | `/api/patients/` | Patient management |
| GET | `/api/patients/?search=name` | Search patients |
| GET | `/api/patients/{id}/prescriptions/` | Patient Rx history |
| CRUD | `/api/templates/` | Prescription templates |
| POST | `/api/templates/{id}/clone/` | Clone template (no original change) |
| GET | `/api/templates/diseases/` | Distinct disease list |
| CRUD | `/api/prescriptions/` | Prescriptions |
| GET | `/api/prescriptions/{id}/print_data/` | Full print payload |
| CRUD | `/api/medicines/` | Medicine database |

---

## 🖥️ Django Admin

```
URL:      http://localhost:8000/admin
Username: admin
Password: admin123
```

---

## 🔄 Template Workflow (Key Feature)

```
1. Create Template  →  Name it + Disease + Medicines + Advice
2. Use Template     →  Loads into Prescription form as editable copy
3. Edit Freely      →  Change doses, add/remove medicines, update advice
4. Save Prescription →  Template usage count increments; original unchanged
5. Clone Template   →  Make a variation without editing the original
```

---

## 🖨️ Print Preview

Prescriptions print with:
- Doctor name, qualifications, registration number
- Clinic name and address (header)
- Patient details: ID, age, gender, blood group
- Visit date and Rx number
- Vitals (BP, pulse, temp, weight)
- Numbered medicine list with dose, frequency, duration, timing
- Advice section
- Allergy warning (if any)
- Follow-up date and doctor signature line

---

## 🔧 Production Deployment

### Switch to PostgreSQL
In `backend/rxmanager/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rxmanager',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Security for production
```python
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['yourdomain.com']
CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
```

### Frontend API URL
In `frontend/index.html`, change line:
```javascript
const API = 'http://localhost:8000/api';
// → change to your production domain
const API = 'https://api.yourdomain.com/api';
```

---

## 📦 Seed Data Included

On first run, the following demo data is pre-loaded:
- **1 Doctor**: Dr. Mohammed Rahman (General Medicine, Dhaka)
- **15 Medicines**: Napa, Azimax, Seclo, Losartan, Metformin, etc.
- **5 Templates**: URTI, Pharyngitis, Hypertension, Diabetes, Gastritis
- **5 Patients**: Sample patients with medical history
- **1 Sample Prescription**: Linked to diabetes template

---

## 📋 Data Models

```
Doctor          → Clinic info for prescription header
Patient         → Auto-ID, age, gender, blood group, allergies, history
Medicine        → Brand name, generic, form, strength
PrescriptionTemplate → Disease templates with medicine list
  └── TemplateMedicine → Individual medicine rows in template
Prescription    → Visit record linked to doctor + patient
  └── PrescriptionMedicine → Individual medicine rows in Rx
```
