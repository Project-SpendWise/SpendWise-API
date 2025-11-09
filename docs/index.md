# SpendWise API Documentation

Welcome to the **SpendWise API** documentation. This API serves as the backend for the SpendWise personal finance tracking application, providing secure authentication, data management, and analytical endpoints.

## Overview

SpendWise API is a RESTful API built with Flask that handles:

- **User Authentication**: Secure registration, login, and JWT-based authentication
- **User Management**: Profile management and password updates
- **Data Security**: Bcrypt password hashing and secure token management
- **CORS Support**: Cross-origin resource sharing for mobile and web clients

## Features

- 🔐 JWT-based authentication with access and refresh tokens
- 🔒 Secure password hashing using bcrypt
- 📊 SQLAlchemy ORM for database management
- 🔄 Database migrations with Flask-Migrate
- ✅ Input validation and sanitization
- 🌐 CORS support for cross-origin requests
- 📝 Standardized API responses
- 📁 File upload and management (PDF, XLSX, XLS, CSV, DOCX)
- 🔗 User-file relationships with ownership verification
- 📂 Organized file storage (date-based + user-based)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:5000`

## API Base URL

```
http://localhost:5000/api
```

## Documentation Structure

- **[Getting Started](getting-started/installation.md)**: Installation and setup guide
- **[API Reference](api/overview.md)**: Complete API endpoint documentation
- **[Authentication](api/authentication.md)**: Authentication flow and token management
- **[File Management](api/endpoints/files.md)**: File upload, download, and management
- **[Models](models/user.md)**: Database models and schemas
- **[Development](development/structure.md)**: Project structure and development guidelines

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0.44
- **Authentication**: Flask-JWT-Extended 4.6.0
- **Migrations**: Flask-Migrate 4.0.5
- **Security**: bcrypt 4.1.2

## Support

For issues, questions, or contributions, please refer to the [Contributing Guide](development/contributing.md).

