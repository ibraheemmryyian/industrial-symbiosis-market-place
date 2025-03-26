# Industrial Symbiosis Marketplace

An AI-powered platform that matches industrial waste producers with potential users, promoting circular economy and sustainability.

## Features

- AI-powered waste matching using Hugging Face models
- User authentication and authorization
- Waste listing and search functionality
- Real-time matching system
- Analytics dashboard
- API documentation

## Tech Stack

- Backend: Python FastAPI
- Frontend: React with TypeScript
- Database: PostgreSQL
- AI: Hugging Face Transformers
- Authentication: JWT

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── services/
├── frontend/
├── tests/
└── requirements.txt
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 