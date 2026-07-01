# RxManager Pro — Multi-Doctor Prescription Management System

A production-grade prescription management system supporting **multiple doctors**, each with their own isolated clinic data, and the ability for each doctor to create **assistant accounts** for delegated data entry.

## Architecture

- **Backend:** Django REST Framework + JWT authentication (`djangorestframework-simplejwt`)
- **Frontend:** Vue 3 (single-file, no build step — open `frontend/index.html` directly)
- **Database:** SQLite (swap to PostgreSQL/MySQL for production by editing `rxmanager/settings.py`)

---

## Role-Based Access Control

Two account types exist, both logging into the **same** login screen:

| Capability | Doctor | Assistant |
|---|:---:|:---:|
| View Dashboard | ✅ | ❌ |
| Register / edit Patients | ✅ | ✅ |
| Add / edit Medicines (catalogue) | ✅ | ✅ |
| Create / view Prescriptions | ✅ | ❌ |
| Create / edit Templates | ✅ | ❌ |
| Manage Assistant accounts | ✅ | ❌ |
| Edit Doctor / Clinic profile | ✅ | ❌ |

**Enforcement is two-layered:**
1. **Frontend** — the sidebar nav only renders the sections a role is allowed to see (`isDoctor` / `isAssistant` computed flags drive `v-if` throughout `index.html`).
2. **Backend** — every API endpoint independently checks the caller's role via `core/permissions.py` (`IsDoctorOnly`, `IsDoctorOrAssistantDataEntry`). The frontend gating is a UX convenience; the backend permissions are the actual security boundary, since a determined user could otherwise call the API directly.

### Data isolation

Every `Patient`, `Prescription`, and `PrescriptionTemplate` row is scoped to a specific `Doctor` via a foreign key. All querysets in `core/views.py` filter by `doctor=get_doctor_for_user(request.user)`, so:
- Doctor A can never see Doctor B's patients, prescriptions, or templates, even via direct API calls with a valid token.
- An Assistant only ever sees data belonging to the one Doctor who created their account (`Assistant.doctor` foreign key).

The `Medicine` catalogue is the one exception — it's a shared, global drug database (like a real pharmacy reference), not scoped per-doctor.

---

## How Account Creation Works

1. **A Doctor self-registers** via the "Register as Doctor" tab on the login screen. This is the *only* way to create a Doctor account — there is no admin approval step needed for the demo, though you could add one.
2. **Once logged in, a Doctor creates Assistant accounts** from the "Manage Assistants" page (sidebar → Settings section). The doctor sets the assistant's username and initial password.
3. **Assistants cannot self-register.** The registration tab is doctor-only by design — this matches the real-world workflow where a clinic owner (doctor) is the one who decides to hire and onboard staff.
4. A Doctor can **deactivate** an assistant (soft-delete — preserves historical data attribution) or **reset their password** at any time from the same page.

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate      # only needed if you deleted db.sqlite3
python manage.py runserver
```

The included `db.sqlite3` already has seed data loaded. To regenerate it from scratch:

```bash
rm db.sqlite3
python manage.py migrate
python seed_data.py
```

### 2. Frontend

Just open `frontend/index.html` in a browser, or serve it with any static file server:

```bash
cd frontend
python -m http.server 5500
# then visit http://localhost:5500
```

The frontend talks to the backend at `http://localhost:8000/api` — this is hardcoded near the top of the `<script>` block in `index.html` as `const API = '...'`. Change it if you deploy the backend elsewhere.

---

## Seeded Demo Accounts

| Role | Username | Password | Clinic |
|---|---|---|---|
| Doctor | `dr.rahman` | `doctor123` | Rahman Medical Center |
| Assistant (works for Dr. Rahman) | `asst.rahim` | `assistant123` | — |
| Doctor (separate clinic, proves data isolation) | `dr.sultana` | `doctor123` | Sultana Women's Care |

Log in as `dr.sultana` and you'll see **completely different** patients and templates than `dr.rahman` — this demonstrates the per-doctor data isolation working correctly.

---

## API Reference (auth-related endpoints)

| Method | Endpoint | Who can call it | Purpose |
|---|---|---|---|
| POST | `/api/auth/register/` | Anyone | Doctor self-registration → returns JWT pair |
| POST | `/api/auth/login/` | Anyone | Login (doctor or assistant) → returns JWT pair + role info |
| POST | `/api/auth/refresh/` | Anyone with a valid refresh token | Get a new access token |
| GET | `/api/auth/me/` | Any logged-in user | Returns role + capability flags, drives frontend UI |
| GET/POST | `/api/assistants/` | Doctor only | List / create assistants under your clinic |
| PATCH/DELETE | `/api/assistants/{id}/` | Doctor only | Update or deactivate an assistant |
| POST | `/api/assistants/{id}/reset-password/` | Doctor only | Reset an assistant's password |

All other endpoints (`/api/patients/`, `/api/prescriptions/`, `/api/templates/`, `/api/medicines/`, `/api/doctors/`, `/api/dashboard/`) require a `Authorization: Bearer <access_token>` header and are subject to the role checks described above.

---

## File Structure

```
backend/
  core/
    models.py            — Doctor, Assistant, Patient, Medicine, Prescription, Template models
    permissions.py        — Role-checking permission classes (the real security boundary)
    auth_serializers.py    — Registration / assistant-creation serializers
    auth_views.py          — Login, register, /me, assistant CRUD endpoints
    serializers.py         — Standard CRUD serializers (Patient, Prescription, etc.)
    views.py                — Standard CRUD viewsets, all doctor-scoped
    admin.py                 — Django admin registrations
  rxmanager/
    settings.py               — JWT config (SIMPLE_JWT), installed apps
    urls.py                    — Root URL config
  seed_data.py                  — Creates demo doctors/assistant/patients/templates
frontend/
  index.html                     — Complete Vue 3 app: login/register screen + main app,
                                    gated by `isLoggedIn` / `isDoctor` / `isAssistant`
```
