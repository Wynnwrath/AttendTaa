# AttendTa v2 &bull; Student Organization Event & Attendance System

AttendTa v2 is a web-based event registration, real-time camera QR attendance verification, digital pass generator, and certificate issuance platform for university student organizations.

---

## 🚀 Quick Start (Run Locally in 5 Seconds)

Zero external dependencies or Node.js required. Runs on standard **Python 3**.

### 1. Clone / Open this Folder
```bash
git clone https://github.com/YOUR_USERNAME/AttendTa-v2.git
cd AttendTa-v2
```

### 2. Start the Local Server
```bash
python server.py
```
*(Or `python3 server.py` on macOS / Linux)*

### 3. Open in Your Browser
Open your browser and navigate to:
👉 [**http://localhost:3000**](http://localhost:3000)

The server will automatically load the **AttendTa v2 Portal Directory** (`index.html`).

---

## 🧭 Live Pages & Route Directory

All routes below assume you are running `server.py` directly from this directory:

| Module / Role | Page Description | Localhost URL |
| :--- | :--- | :--- |
| **Gateway** | Central Campus Showcase & Gateway | [`/index.html`](http://localhost:3000/index.html) |
| **Authentication** | Student & Officer Sign In | [`/account/login.html`](http://localhost:3000/account/login.html) |
| **Registration** | Student Membership Request | [`/account/register.html`](http://localhost:3000/account/register.html) |
| **Approvals** | Officer Account Approval Queue | [`/account/approvals.html`](http://localhost:3000/account/approvals.html) |
| **Student** | Browse Event Sessions & RSVP | [`/student/events.html`](http://localhost:3000/student/events.html) |
| **Student** | Event Details & Seating Dossier | [`/student/details.html?eventId=1`](http://localhost:3000/student/details.html?eventId=1) |
| **Student** | **QR Pass Generator (with Logo Emblem)** | [`/student/passes.html`](http://localhost:3000/student/passes.html) |
| **Student** | Attendance History & Academic Vault | [`/student/history.html`](http://localhost:3000/student/history.html) |
| **Officer** | **Live Attendance Phone Camera Kiosk** | [`/kiosk/index.html`](http://localhost:3000/kiosk/index.html) |
| **Officer** | Event Operations & Publishing Hub | [`/events/index.html`](http://localhost:3000/events/index.html) |
| **Officer** | Create Event Dedicated Form | [`/events/create.html`](http://localhost:3000/events/create.html) |
| **Officer** | Attendee Rosters & Waitlist Overrides | [`/events/details.html`](http://localhost:3000/events/details.html) |
| **Officer** | Master Member Records Directory | [`/masterdata/members.html`](http://localhost:3000/masterdata/members.html) |
| **Officer** | Venue & Facilities Management | [`/masterdata/venues.html`](http://localhost:3000/masterdata/venues.html) |
| **Officer** | Add Venue Dedicated Form | [`/masterdata/venue-create.html`](http://localhost:3000/masterdata/venue-create.html) |
| **Officer** | Batch Certificate Issuance | [`/certificates/index.html`](http://localhost:3000/certificates/index.html) |
| **Public** | Official Academic Certificate (Print PDF) | [`/certificates/view.html`](http://localhost:3000/certificates/view.html) |
| **Officer** | Turnout Demographics & CSV Reports | [`/reports/participation.html`](http://localhost:3000/reports/participation.html) |
| **Admin** | Officer & Role Management | [`/admin/users.html`](http://localhost:3000/admin/users.html) |
| **Admin** | Appoint Officer & 10 Scope Checkmarks | [`/admin/user-create.html`](http://localhost:3000/admin/user-create.html) |
| **Admin** | System Security Activity Audit Logs | [`/admin/auditlogs.html`](http://localhost:3000/admin/auditlogs.html) |

---

## 🛠 Key System Features

- **Phone Camera Scanner Kiosk (`/kiosk/index.html`):**
  - Allows event officers to use their phone/tablet camera (Safari iOS / Chrome Android) to scan student QR passes in real time.
  - Corner reticles, scanning laser guide, and manual student ID fallback.
- **Dynamic Pass Generator with Emblem (`/student/passes.html`):**
  - Instant high-contrast QR generation embedding the official **AttendTa logo emblem** at the center with high error correction.
- **Officer Appointments & Granular Permissions (`/admin/`):**
  - 4 Role Authority presets (`Administrator`, `Chapter Officer`, `Committee Staff`, `Student Member`) plus 10 granular operational capability checkboxes.
- **ASP.NET Core Razor Pages Viable:**
  - Standard semantic `<form method="post">` blocks that map directly to `.cshtml` Razor Page `OnPostAsync` handlers and Model Binding.
- **Client-Side Reactive Synchronization:**
  - Uses `localStorage` database simulation so updates made in one tab reflect across other open tabs.

---

## 💻 Tech Stack
- **Frontend:** Semantic HTML5, Tailwind CSS, Modern ES6+ JavaScript.
- **Libraries (CDN):** Tailwind CSS, `jsQR` (Camera decoding), `qrcodejs` (QR rendering).
- **Backend Compatibility:** ASP.NET Core Razor Pages (.NET 8/9).
- **Server:** Python 3 Standard Library (`http.server.ThreadingHTTPServer`).

---

&copy; 2026 USTP Student Organization Council &bull; AttendTa Event Management System.
