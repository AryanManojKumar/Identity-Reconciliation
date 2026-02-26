# Identity Reconciliation Service

Backend service for linking customer identities across multiple purchases using different contact information.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your database URL:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

3. Run the application:
```bash
python app.py
```

Server starts at: http://localhost:5000

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Endpoints

### POST /identify

Identifies and consolidates customer contact information.

**Request:**
```json
{
  "email": "mcfly@hillvalley.edu",
  "phoneNumber": "123456"
}
```

**Response:**
```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["lorraine@hillvalley.edu", "mcfly@hillvalley.edu"],
    "phoneNumbers": ["123456"],
    "secondaryContactIds": [2]
  }
}
```

### GET /health

Health check endpoint.

## Testing Scenarios

Use the Swagger UI at `/docs` to test these scenarios:

1. **New customer**: Send unique email + phone → Creates primary contact
2. **Returning customer**: Send same phone, new email → Creates secondary contact
3. **Query existing**: Send known email or phone → Returns consolidated info
4. **Merge identities**: Link two separate primaries → Converts newer to secondary

## Deployment (Render)

1. Create PostgreSQL database in Render
2. Create Web Service connected to your repo
3. Set environment variable:
   - `DATABASE_URL`: (Internal Database URL from Render)
4. Deploy

Build Command: `pip install -r requirements.txt`
Start Command: `python app.py`
