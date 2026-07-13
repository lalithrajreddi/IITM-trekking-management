# Trekking Management Application

A robust web-based platform designed to streamline the organization, management, and booking of trekking expeditions. The application provides dedicated, role-based dashboards for Administrators, Trek Staff, and Trekkers, ensuring secure and centralized tracking of all activities.

## Technologies Used
- **Backend:** Flask (Python)
- **Database:** SQLite (managed via Flask-SQLAlchemy)
- **Frontend:** Jinja2 Templating, Custom CSS, Bootstrap 5
- **Constraint:** Zero client-side JavaScript is used for core logic or validation. All business logic and capacity checks are handled securely on the server-side.

## How to Run Locally

1. **Activate Virtual Environment**
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Flask Application**
   ```powershell
   python app.py
   ```
   The server will start locally. Access the application by opening a web browser and navigating to `http://127.0.0.1:5000/`.

## Default Access Credentials
A default Administrator account is automatically seeded into the database the very first time you run the application.
- **Admin Email:** `admin@trekking.com`
- **Password:** `admin123`
