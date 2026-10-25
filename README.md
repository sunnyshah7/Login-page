# Login Page

A full-stack account sign-in and registration flow built with React and FastAPI. The authentication screens are part of the ChatFlow demo today, and can serve as a starting point for adding account access to other projects.

> This repository is not yet a standalone React package. The current screens use ChatFlow branding and the app opens the ChatFlow home screen after sign-in. Adapt the branding, callbacks, API URL, and post-login destination when reusing them.

## Features

- Email and password sign-in with field validation and visible request errors.
- Account registration with name, email, password confirmation, and terms acceptance.
- Password hashing on the backend and short-lived JWT access tokens.
- Authenticated current-user endpoint that returns public profile fields only.
- Duplicate-account handling and consistent invalid-credentials responses.
- Responsive ChatFlow frontend, plus the demo home, chat, notifications, and settings screens.
- Backend tests for sign-in, registration, JWT validation, and malformed requests.

## Stack

- Frontend: React 19, Vite, and `lucide-react`.
- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, PyJWT, and `pwdlib`.
- Tests: pytest and FastAPI's `TestClient`.

## Requirements

- Python 3.10 or newer. Python 3.12 is a good local choice for the pinned PostgreSQL driver.
- Node.js and npm.
- PostgreSQL, with a database and role matching your `DATABASE_URL`.

## Local Setup

### 1. Configure the backend

From the repository root:

```bash
cd chatflow_backend
python3.12 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Create `chatflow_backend/.env` with your local database connection and a unique signing key. Do not commit this file.

```dotenv
DATABASE_URL=postgresql+psycopg2://<db_user>:<db_password>@localhost:5432/<db_name>
JWT_SECRET_KEY=<output-of-openssl-rand-hex-32>
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Generate a signing key with:

```bash
openssl rand -hex 32
```

Make sure PostgreSQL is running and the database in `DATABASE_URL` already exists. Start the API from `chatflow_backend`:

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

In another terminal, from the repository root:

```bash
cd chatflow_frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`. The login and signup screens use `http://127.0.0.1:8000` by default. To point them to another API, create `chatflow_frontend/.env.local`:

```dotenv
VITE_API_URL=https://your-api.example.com
```

Restart the Vite server after changing environment variables.

## Authentication API

All routes are prefixed with `/auth`.

| Method | Route | Purpose | Typical responses |
| --- | --- | --- | --- |
| `GET` | `/health` | Auth service health check | `200` |
| `POST` | `/signup` | Create an account using `name`, `email`, and `password` | `201`, `409` for an existing email, `422` for invalid input |
| `POST` | `/login` | Verify credentials and return an access token | `200`, `401` for invalid credentials, `422` for invalid input |
| `GET` | `/me` | Return the authenticated user's public profile | `200`, `401` for a missing or invalid token |

A successful login returns a bearer access token:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

Send it to `/auth/me` in the `Authorization` header:

```http
Authorization: Bearer <jwt>
```

Tokens currently expire after 15 minutes. The API does not provide refresh tokens.

## Reusing the Login Flow

1. Copy `chatflow_frontend/src/screens/Login.jsx` and `Signup.jsx`, along with the related auth styles from `chatflow_frontend/src/styles.css`.
2. Replace the ChatFlow name, text, and visual assets with your product's branding.
3. Keep or adapt the `onLogin`, `onSignup`, `onBack`, and `onCreated` callbacks to match your router and application state.
4. Set `VITE_API_URL` to the backend that implements the documented auth routes, or change the request paths and payloads to match your API.
5. Add session persistence and token lifecycle handling appropriate for your application before using the flow in production.

The current UI validates a successful login by requesting `/auth/me`, then passes the user ID to its parent. It does not persist the access token or restore a session after a page reload. The Google sign-in and password-recovery buttons are visual placeholders; the signup photo control does not upload a file. Those features need their own provider, backend routes, and state handling before they are functional.

## Development Checks

Run backend tests from `chatflow_backend`:

```bash
python -m pytest -q
```

Build the frontend from `chatflow_frontend`:

```bash
npm run build
```

## Security Notes

- Keep `.env` and `.env.local` files out of Git. The repository ignores them.
- Use a unique, randomly generated `JWT_SECRET_KEY` for each environment and store production secrets in your deployment's secret manager.
- Serve production traffic over HTTPS and restrict `CORS_ORIGINS` to the frontend origins you control.
- Do not store passwords in plaintext. The backend hashes passwords before saving them.
- Review token storage and renewal choices for your app's threat model; this demo does not implement refresh tokens or persistent client sessions.
