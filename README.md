# Memoria

A modern note-taking application with AI-powered idea generation, user authentication, and favorites management.

English | [日本語](README.ja.md)

## Features

- 📝 Create, edit, and delete notes with rich text support
- ⭐ Favorite notes for quick access
- 🤖 AI-powered idea generation (OpenAI, Anthropic, Google Gemini)
- 🔐 Secure user authentication with JWT
- 📤 Export notes as text files
- 🎨 Clean and responsive UI built with React and Tailwind CSS
- 🚀 Fast and modern tech stack

## Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- React Router
- Zustand (state management)
- Axios
- Tailwind CSS

### Backend

- FastAPI
- Python 3.11+
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- OpenAI / Anthropic / Google Gemini APIs

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or use Docker)

### Local Development

1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/memoria-app.git
cd memoria-app
```

2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env
# Edit .env with your database credentials and API keys
uvicorn app.main:app --reload
```

3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

4. Access the application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/memoria_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173

# Optional: AI API Keys (for local development only)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key
```

**Note:** AI features are disabled in production deployment to prevent unexpected API costs. To use AI idea generation, run the application locally with your own API keys.

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions using Vercel (frontend) and Render (backend).

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## License

MIT License - feel free to use this project for learning and personal projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
