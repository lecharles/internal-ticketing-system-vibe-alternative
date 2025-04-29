# Internal Ticket Management System

A lightweight, self-hosted alternative to JIRA for internal software development tracking and planning.

## Overview

This system provides essential project management and ticket tracking functionality while maintaining simplicity and ease of use. It's designed to run on a single Postgres instance with a Flask backend, making it easy to deploy and maintain.

## Core Features

- **Ticket Management**
  - Create, update, and delete tickets
  - Assign tickets to team members
  - Set priority levels and status
  - Add comments and attachments
  - Track time estimates and actual time spent

- **Project Organization**
  - Create and manage multiple projects
  - Organize tickets into sprints
  - Kanban board view for visual tracking
  - Simple backlog management

- **User Management**
  - Role-based access control (Admin, Project Lead, Developer, Viewer)
  - Team member profiles
  - Activity tracking

- **Reporting**
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
- CSS3 (with Tailwind CSS)
- JavaScript (Vanilla JS + Alpine.js for interactivity)
- No complex build process required

### Infrastructure
- Single PostgreSQL instance
- Runs on any WSGI-compatible server
- Minimal resource requirements

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd internal-jira
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL
- Create a new PostgreSQL database
- Update the database configuration in `config.py`

5. Initialize the database
```bash
flask db upgrade
```

6. Start the development server
```bash
flask run
```

## Configuration

The application can be configured through environment variables or a `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
DEBUG=True
```

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

## Project Structure

```
internal-jira/
├── app/
│   ├── models/         # Database models
│   ├── views/          # Route handlers
│   ├── templates/      # Jinja2 templates
│   ├── static/         # Static files
│   └── utils/          # Helper functions
├── migrations/         # Database migrations
├── tests/             # Test suite
├── config.py          # Configuration
├── requirements.txt   # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Security Considerations

- All passwords are hashed using bcrypt
- CSRF protection enabled
- Session management with secure cookies
- Input validation and sanitization
- Regular security updates for dependencies

## Backup and Maintenance

- Regular database backups recommended
- Automated backup scripts provided
- Database optimization guidelines included
- Monitoring setup instructions available

## License

Internal use only. All rights reserved.

## Support

For internal support, contact the development team.

---

This project aims to provide a streamlined, maintainable alternative to JIRA while keeping the essential features needed for effective software development tracking. 