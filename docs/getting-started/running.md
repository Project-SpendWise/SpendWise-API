# Running the Server

This guide covers different ways to run the SpendWise API server.

## Development Mode

### Using Python Directly

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` with debug mode enabled.

### Using Flask CLI

```bash
export FLASK_APP=app.py
flask run
```

Or with custom host and port:

```bash
flask run --host=0.0.0.0 --port=5000
```

## Production Mode

### Using Gunicorn (Recommended)

Install Gunicorn:

```bash
pip install gunicorn
```

Run with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

Options:
- `-w 4`: Number of worker processes
- `-b 0.0.0.0:5000`: Bind address and port
- `app:create_app()`: Application factory

### Using Waitress (Windows-friendly)

Install Waitress:

```bash
pip install waitress
```

Run with Waitress:

```python
from waitress import serve
from app import create_app

app = create_app('production')
serve(app, host='0.0.0.0', port=5000)
```

## Docker Deployment

### Dockerfile Example

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=postgresql://user:pass@db/spendwise
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=spendwise
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Environment-Specific Running

### Development

```bash
export FLASK_ENV=development
python app.py
```

### Production

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret-key
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Testing

```bash
export FLASK_ENV=testing
pytest  # If you have tests
```

## Health Check

After starting the server, verify it's running:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "SpendWise API"
}
```

## Common Issues

### Port Already in Use

If port 5000 is already in use:

```bash
# Find the process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Use a different port
flask run --port=5001
```

### Database Connection Errors

Ensure the database is accessible and the connection string is correct:

```bash
# Test SQLite database
sqlite3 instance/spendwise.db

# Test PostgreSQL connection
psql $DATABASE_URL
```

### CORS Issues

If you encounter CORS errors, check your `CORS_ORIGINS` configuration in `config.py` or environment variables.

## Process Management

### Using systemd (Linux)

Create `/etc/systemd/system/spendwise-api.service`:

```ini
[Unit]
Description=SpendWise API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/spendwise-api
Environment="PATH=/var/www/spendwise-api/venv/bin"
ExecStart=/var/www/spendwise-api/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable spendwise-api
sudo systemctl start spendwise-api
```

### Using PM2 (Node.js process manager)

Install PM2:

```bash
npm install -g pm2
```

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'spendwise-api',
    script: 'gunicorn',
    args: '-w 4 -b 0.0.0.0:5000 app:create_app()',
    interpreter: 'python',
    env: {
      FLASK_ENV: 'production'
    }
  }]
}
```

Run:

```bash
pm2 start ecosystem.config.js
```

