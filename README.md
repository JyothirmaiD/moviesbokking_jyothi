# 🎬 CineVerse — Movie Ticket Booking & Community Review Portal
### Capstone Project 5 • Django Full-Stack Final Project — Student Assignment

A modern full-stack cinema web application featuring real-time showtime scheduling, an interactive **5×8 auditorium seat selection matrix**, dynamic ticket pricing calculation, community reviews with **1–5 star ratings**, and server-side duplicate booking prevention.

---

## 🛠️ Mandatory Technology Stack
- **Backend**: Python 3.11+, Django 5.x / 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3` default, zero external DB dependencies)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Production Server**: Gunicorn
- **Static Assets**: WhiteNoise
- **Deployment Platform**: Render (via `render.yaml` Blueprint)

---

## 📁 Project Structure

```text
Project/
├── manage.py                     # Django management utility
├── requirements.txt              # Production Python dependencies
├── render.yaml                   # Render Blueprint configuration
├── create_superuser.py           # Automated superuser initialization
├── seed_data.py                  # Demo data seeder (movies, showtimes, reviews)
├── .gitignore                    # Version control ignore rules
├── README.md                     # Complete project documentation
├── cinema_portal/                # Django core project package
│   ├── __init__.py
│   ├── settings.py               # Configured for WhiteNoise & Render
│   ├── urls.py                   # Master URL routing
│   ├── wsgi.py                   # WSGI application for Gunicorn
│   └── asgi.py                   # ASGI application
└── movies/                       # Main cinema application
    ├── __init__.py
    ├── apps.py                   # App configuration
    ├── admin.py                  # Django Admin models registration
    ├── forms.py                  # SeatBookingForm & MovieReviewForm with validation
    ├── models.py                 # Movie, Showtime, SeatBooking, MovieReview models
    ├── urls.py                   # Cinema views URL routing
    ├── views.py                  # Business logic & view controllers
    ├── migrations/
    │   └── __init__.py
    ├── static/
    │   ├── css/
    │   │   └── cinema.css        # Cinema dark aesthetic & glowing visual system
    │   └── js/
    │       └── seat_booking.js   # 5x8 seat selection matrix & pricing engine
    └── templates/
        └── movies/
            ├── base.html                 # Master layout with navbar & footer
            ├── movie_list.html           # Catalog with search & genre filter
            ├── movie_detail.html         # Movie page, showtimes, community reviews
            ├── book_seats.html           # 5x8 Interactive seat matrix & checkout
            ├── booking_confirmation.html # Printable cinema ticket voucher
            └── my_bookings.html          # Ticket lookup by booking ref or email
```

---

## 🚀 Step-by-Step Local Setup & Execution Guide

Follow these exact steps in your terminal (PowerShell, Command Prompt, or bash):

### Step 1: Create and Activate Virtual Environment

**On Windows (PowerShell or CMD):**
```powershell
python -m venv venv
venv\Scripts\activate
```

*(On macOS/Linux):*
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 3: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
*This automatically initializes Django's default SQLite database (`db.sqlite3`).*

---

### Step 4: Create Admin Superuser
You can create an admin automatically using our helper script:
```bash
python create_superuser.py
```
*(Default credentials created: Username: `admin` | Password: `admin12345`)*

Or manually create one using Django:
```bash
python manage.py createsuperuser
```

---

### Step 5: Populate Realistic Sample Data
Populate movies, showtimes across 3 days, pre-booked seats, and community reviews:
```bash
python seed_data.py
```

---

### Step 6: Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Cinema Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Management**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **My Bookings Lookup**: [http://127.0.0.1:8000/my-bookings/](http://127.0.0.1:8000/my-bookings/)

---

## 🌐 Render Public Deployment Guide

This project is pre-configured with `render.yaml`, `WhiteNoise`, and `Gunicorn`.

### 1. Initialize Git Repository & Push to GitHub
```bash
git init
git add .
git commit -m "feat: complete capstone movie ticket booking and community review portal"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### 2. Deploy on Render
1. Log in to [render.com](https://render.com/).
2. Click **New +** → **Blueprint** (or **Web Service**).
3. Connect your GitHub repository.
4. Render will automatically read `render.yaml`:
   - **Runtime**: Python 3.11.0
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py && python seed_data.py
     ```
   - **Start Command**:
     ```bash
     python manage.py migrate && python create_superuser.py && gunicorn cinema_portal.wsgi:application
     ```
5. Add the Environment Variable in Render:
   - `SECRET_KEY`: `<your-secure-random-secret-key>`
   - `RENDER`: `True`
6. Click **Apply / Deploy**.

Once deployment finishes, open your live `https://<service-name>.onrender.com` URL.

---

## 🔒 Security & Business Rules Compliance
- ✅ **Server-Side Duplicate Seat Prevention**: Selected seats are verified against all existing reservations for the requested showtime during `form.clean_selected_seats()`. Any overlapping seat raises a validation error.
- ✅ **Server-Authoritative Price Calculation**: `total_paid` is recalculated on the backend as `len(seats) * showtime.ticket_price`.
- ✅ **1–5 Star Rating Range Validation**: Enforced via Django validators `MinValueValidator(1)` and `MaxValueValidator(5)`.
- ✅ **CSRF Protection**: Enabled on all POST forms (`{% csrf_token %}`).
