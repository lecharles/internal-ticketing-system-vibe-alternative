# Internal Ticketing System (Vibe Alternative)

A modern, Flask-based ticketing system with PostgreSQL backend and Tailwind CSS UI. This project provides a lightweight, customizable issue tracking system designed for internal team use.

## Features

- 🔐 User Authentication & Authorization
- 📋 Project Management
- 🎫 Ticket System
- 💬 Comments & Discussions
- 📱 Responsive Design
- 🎨 Modern UI with Tailwind CSS

## Tech Stack

- Backend: Flask
- Database: PostgreSQL
- ORM: SQLAlchemy
- Frontend: Tailwind CSS
- Authentication: Flask-Login

## Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for Tailwind CSS)

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

6. Run the development server:
   ```bash
   flask run
   ```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── auth/
│   ├── main/
│   ├── tickets/
│   ├── models/
│   ├── static/
│   └── templates/
├── migrations/
├── tests/
├── requirements.txt
└── README.md
```

## Development

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

3. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request

## Testing

Run tests with:
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation and community
- Tailwind CSS team
- All contributors

## Support

For support, please open an issue in the GitHub repository.

---

Built with ❤️ using Flask and modern web technologies.