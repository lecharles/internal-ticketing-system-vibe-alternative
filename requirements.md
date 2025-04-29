Internal Ticketing System Requirements Document
This document outlines the requirements for an internal ticketing system designed to replace JIRA for software development planning and tracking. The system will be built using Flask and PostgreSQL, prioritizing simplicity and essential functionality.

1. System Overview
A lightweight, self-hosted alternative to JIRA for internal software development tracking and planning. This system provides essential project management and ticket tracking functionality while maintaining simplicity and ease of use. It's designed to run on a single Postgres instance with a Flask backend, making it easy to deploy and maintain.

2. Goals
Simplify task tracking and sprint planning.
Eliminate dependency on external SaaS (JIRA).
Control data privacy and cost (internal hosting on PostgreSQL + Flask).
Provide a simple, fast, easy-to-use web-based interface.
3. Stakeholders
Role	Responsibilities
Dev team	Users of the ticket system (create, update, track tasks)
Tech Lead / PM	Sprint management (prioritize, assign tickets)
Engineering Ops	Maintain server, backups, DB tuning

Export to Sheets
4. Problem
Current use of JIRA is:

Overcomplicated for small, fast-moving teams.
Slow and costly to maintain.
Too heavy for our lightweight sprint workflow.
We need a minimal system that supports tickets, states, comments, and basic reporting — nothing more.

5. Solution (High-Level Overview)
Backend: Flask server (Python 3.11+), REST API.
Frontend: Minimal HTML + Bootstrap (or Tailwind) based UI. HTML5, CSS3 (with Tailwind CSS), JavaScript (Vanilla JS + Alpine.js for interactivity). No complex build process required.
Database: Single PostgreSQL instance (PostgreSQL 15+ recommended).
6. Requirements
6.1. Functional Requirements
Ticket Management
Create, update, and delete tickets.
Assign tickets to team members.
Set priority levels (Low, Medium, High, Critical).
Set status (Backlog, To Do, In Progress, Done, Blocked, Review).
Add comments to tickets.
Add attachments to tickets (optional).
Track time estimates and actual time spent.
Tickets can transition between predefined states (workflow).
Search and filter tickets by assignee, state, sprint.
Project Organization
Create and manage multiple projects.
Organize tickets into sprints.
Kanban board view for visual tracking.
Simple backlog management.
Assign users to projects.
User Management
Role-based access control (Admin, Project Lead, Developer, Viewer, Project Manager).
Team member profiles with contact information.
Activity tracking.
User registration and authentication.
Reporting
Sprint velocity tracking.
Basic burndown charts.
Time tracking reports.
Custom filters and saved searches.
Basic reporting (tickets by status, user workload).
Sprint Planning
Create time-bounded sprints.
Assign tickets to sprints.
Sprint retrospective notes.
System must display a Sprint View (all tickets grouped by Sprint).
Users can create, edit, and close Sprints.
Dashboard
Overview of assigned tickets.
Project progress metrics.
Recent activity feed.
Personal to-do list.
6.2. Non-Functional Requirements
Performance: Page load times under 2 seconds. System must be lightweight and fast (<1s response times for standard queries).
Security: HTTPS, secure password storage (hashed using bcrypt), input validation and sanitization. CSRF protection enabled. Session management with secure cookies. Regular security updates for dependencies.
Scalability: Support for at least 20 concurrent users, ideally up to 50 concurrent users.
Reliability: Regular database backups recommended. Automated backup scripts provided. Database optimization guidelines included.
Maintainability: Well-documented code, modular design.
System must persist data securely in PostgreSQL.
System must allow basic admin actions (user management if needed later).
7. Acceptance Criteria
A new user can register/login (or we can use basic auth for first version).
A ticket can be created, edited, moved through states, and commented on.
Users can view tickets by Sprint and Status.
A Sprint can be started and closed manually.
All changes are visible immediately after action.
System successfully deployed to production environment.
All team members trained and using the system.
Reduction in ticket management overhead.
Improved visibility into project status and team workload.
8. User Interface Requirements
Clean, minimalist design.
Responsive layout for desktop use.
Kanban board view for tickets.
List view with filtering options.
Simple reports and visualizations.
Very basic UX with a Dashboard (List of tickets with filters), Ticket View (Title, description, state, assignee, comments), Sprint View (Grouped tickets), Create Ticket (Simple form), Edit Ticket (Same form, editable fields), Comment box (On ticket view).
9. Out of Scope
No mobile app.
No sophisticated permission system (basic login is enough initially).
No API integrations (e.g., no GitHub auto-ticket creation for now).
10. Instrumentation (Optional)
Basic logging of CRUD operations.
Metrics: # tickets per sprint, average time to close a ticket.
11. Dependencies
Python 3.11+.
Flask (2.3+ recommended).
SQLAlchemy (2.0+ recommended).
PostgreSQL 14+ (15+ recommended).
Flask-Login for authentication.
Flask-SQLAlchemy for ORM.
Flask-Migrate for database migrations.
Basic Bootstrap or Tailwind frontend (optional: HTMX for interactivity).
12. Future Considerations (Version 2.0)
Email notifications.
Time tracking.
Custom workflows.
Integration with version control systems.
Advanced reporting and analytics.
API for third-party integrations.
Labels / tags.
Audit trail (simple history log).
13. Database Schema (High-Level)
Users (id, username, email, password_hash, role, etc.).
Projects (id, name, description, created_at, etc.).
Tickets (id, title, description, status, priority, assignee_id, reporter_id, project_id, created_at, updated_at, etc.).
Comments (id, ticket_id, user_id / author_id, content, created_at).
Sprints (id, project_id, name, start_date, end_date, status / closed).
Attachments (id, ticket_id, filename, file_path, uploaded_by, uploaded_at).