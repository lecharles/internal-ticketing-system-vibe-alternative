# Internal Ticketing System (Vibe Alternative)

A modern, Flask-based ticketing system designed as a lightweight, self-hosted alternative to JIRA for internal software development tracking and planning. Built with PostgreSQL backend and Tailwind CSS UI.

## Core Features

- **Ticket Management** 🎫
  - Create, update, and delete tickets
  - Assign tickets to team members
  - Set priority levels and status
  - Add comments and attachments
  - Track time estimates and actual time spent

- **Project Organization** 📋
  - Create and manage multiple projects
  - Organize tickets into sprints
  - Kanban board view for visual tracking
  - Simple backlog management

- **User Management** 🔐
  - Role-based access control (Admin, Project Lead, Developer, Viewer)
  - Team member profiles
  - Activity tracking
  - Secure authentication

- **Reporting** 📊
  - Sprint velocity tracking
  - Basic burndown charts
  - Time tracking reports
  - Custom filters and saved searches

## Technical Stack

### Backend
- Python 3.11+
- Flask 2.3+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Flask-Login for authentication
- Flask-SQLAlchemy for ORM
- Flask-Migrate for database migrations

### Frontend
- HTML5
- CSS3 with Tailwind CSS
- JavaScript (Vanilla JS + Alpine.js for interactivity)
- Responsive Design
- Modern UI components

### Infrastructure
- Single PostgreSQL instance
- Runs on any WSGI-compatible server
- Minimal resource requirements

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lecharles/internal-ticketing-system-vibe-alternative.git
cd internal-ticketing-system-vibe-alternative
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/internal_ticketing_dev
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Start the development server:
```bash
flask run
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── auth/          # Authentication views and forms
│   ├── main/          # Core application views
│   ├── tickets/       # Ticket management
│   ├── models/        # Database models
│   ├── static/        # Static files (CSS, JS)
│   └── templates/     # Jinja2 templates
├── migrations/        # Database migrations
├── tests/            # Test suite
├── config.py         # Configuration
├── requirements.txt  # Production dependencies
└── README.md
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

4. Make your changes and commit:
```bash
git add .
git commit -m "Add your feature description"
```

5. Push to your branch:
```bash
git push origin feature/your-feature-name
```

## Testing

Run the test suite with:
```bash
python -m pytest
```

For coverage report:
```bash
pytest --cov=app tests/
```

## Security Considerations

- All passwords are hashed using bcrypt
- CSRF protection enabled
- Session management with secure cookies
- Input validation and sanitization
- Regular security updates for dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.

## Acknowledgments

- Flask documentation and community
- Tailwind CSS team
- All contributors

---

Built with ❤️ using Flask and modern web technologies.
