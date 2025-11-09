# Installation

This guide will help you set up the SpendWise API on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/SpendWise-API.git
cd SpendWise-API
```

## Step 2: Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-Migrate
- bcrypt
- python-dotenv
- SQLAlchemy

## Step 4: Environment Variables

Create a `.env` file in the root directory (optional for development):

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///spendwise.db
CORS_ORIGINS=*
```

!!! warning "Production Security"
    In production, always set strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`. Never commit these to version control.

## Step 5: Initialize the Database

The database will be automatically created when you first run the application:

```bash
python app.py
```

This will create the SQLite database file at `instance/spendwise.db` with all required tables.

Alternatively, you can manually create the database:

```python
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created successfully")
```

Or using Flask CLI (if migrations are set up):

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Step 6: Verify Installation

Run the health check endpoint:

```bash
curl http://localhost:5000/api/health
```

You should receive:

```json
{
  "status": "healthy",
  "service": "SpendWise API"
}
```

## Next Steps

- Read the [Configuration Guide](configuration.md) to customize your setup
- Check out [Running the Server](running.md) for deployment options
- Explore the [API Reference](../api/overview.md) to start using the API

