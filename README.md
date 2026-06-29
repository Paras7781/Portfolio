# Portfolio with FastAPI Backend

A modern portfolio website with a lightweight FastAPI backend for serving the site and handling contact form submissions.

## Features
- Responsive portfolio site
- FastAPI health endpoint and contact API
- Contact form submission through a real backend endpoint
- Local development server with hot reload support

## Run locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   uvicorn main:app --reload
   ```
3. Open http://127.0.0.1:8000/

## API endpoints
- GET /api/health
- POST /api/contact

## Email setup
To send real emails from the contact form, set these environment variables before starting the server:

```bash
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@example.com
SMTP_TO=your-email@example.com
```

If these are not configured, the contact form will still be accepted locally and return a success message without sending an email.

## Testing
```bash
pytest -q
```
