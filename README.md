# 🌱 Habit Tracker

A full-stack web app to track your daily habits, built with Python and Flask.

👉 **[Live Demo](https://habit-tracker-production-d737.up.railway.app)**

---

## Features

- User signup & login with secure password hashing
- Add and delete personal habits
- Mark habits as complete each day
- Streak counter — track how many days in a row you've kept up
- 21-day heatmap visualization
- Weekly completion percentage stats
- Each user sees only their own habits

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL (Railway)
- **Frontend:** HTML, CSS
- **Auth:** Session-based with Werkzeug password hashing
- **Deployment:** Railway

## Running Locally

1. Clone the repo
```bash
   git clone https://github.com/MicolDellaColletta/habit-tracker.git
   cd habit-tracker
```

2. Install dependencies
```bash
   pip3 install -r requirements.txt
```

3. Set up your database and environment variable
```bash
   export DATABASE_URL=your_postgresql_url
```

4. Run the app
```bash
   python3 app.py
```

5. Open http://localhost:5000

## About

Built by **Clarissa Micol Della Colletta** — a self-taught developer based in Porto, Portugal.
Currently learning Python, Flask, Linux and IT.

[Portfolio](https://micoldellacolletta.github.io) · [GitHub](https://github.com/MicolDellaColletta)