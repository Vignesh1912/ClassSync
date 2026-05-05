# ClassSync

ClassSync is a comprehensive classroom management and attendance tracking platform designed to streamline the interaction between teachers and students. It features a robust authentication system, real-time GPS-based attendance tracking, assignment management, and a dynamic timetable system.

## Features

- **Role-Based Access Control**: Separate dashboards and functionalities for Teachers and Students.
- **Secure Authentication**: User registration and login powered by secure email verification, bcrypt hashing, and OTP features.
- **Advanced Attendance Management**: 
  - Class-section-based attendance filtering.
  - Mobile-responsive, GPS-based attendance tracking for students.
- **Assignment Tracking**: Teachers can create and manage assignments; students can easily view pending and completed work.
- **Timetable System**: Effortlessly manage class schedules and slot creation.
- **InsForge Integration**: Deep integration with InsForge (Backend-as-a-Service) for robust data management, authentication, and deployment.

## Technology Stack

- **Backend Framework**: Python / [Flask](https://flask.palletsprojects.com/)
- **Database**: PostgreSQL (managed via InsForge / Render.com)
- **ORM & Migrations**: Flask-SQLAlchemy, Flask-Migrate
- **Authentication**: Flask-Login, Flask-WTF, bcrypt, Flask-Mail (for verification)
- **Task Scheduling**: APScheduler
- **Frontend**: HTML5, CSS3, JavaScript (Jinja2 templates)
- **Deployment & Hosting**: [Render.com](https://render.com) / [InsForge](https://insforge.app)

## Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for InsForge MCP tools and SDKs)

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd classSync
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory based on `.env.example` and fill in the required database credentials, mail settings, and InsForge keys.

5. **Database Initialization**:
   Apply database migrations to set up your PostgreSQL schema:
   ```bash
   flask db upgrade
   ```
   *Optional:* Run the seed script to populate the database with initial test data:
   ```bash
   python seed.py
   ```

6. **Run the Application**:
   You can run the application using the Flask CLI:
   ```bash
   flask run
   ```
   Or use the provided startup scripts:
   - On Windows: `start_website.bat`
   - On macOS/Linux: `./start_website.sh`

## Deployment

The application is configured for seamless deployment on Render.com using the included `render.yaml` specification. It also utilizes InsForge's platform for deploying frontend/backend components and managing metadata.

## Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.
