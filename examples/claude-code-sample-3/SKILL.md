# Skill: Express.js JWT API with PostgreSQL and Docker

> Builds a production-style Express.js REST API with JWT authentication, a PostgreSQL database, layered middleware, and Docker Compose for local development.

---

## When to use

When the user asks to scaffold a secure Node.js/Express REST API with login/registration, protected routes, a relational database, and containerized local development.

---

## Prerequisites

Make sure Node.js 18+ and npm are installed, plus Docker and Docker Compose for the database.

Set these environment variables (the app reads them at boot):

- `$JWT_SECRET` — secret used to sign access tokens
- `$DATABASE_URL` — PostgreSQL connection string
- `$PORT` — port the API listens on (default 3000)

## Steps

Initialize the project and install dependencies:

```bash
npm init -y
npm install express jsonwebtoken bcrypt pg dotenv
npm install --save-dev nodemon
```

Create the file `src/db.js` for the PostgreSQL connection pool:

```javascript
const { Pool } = require('pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports = { pool };
```

Create `src/middleware/auth.js`, a middleware that verifies the JWT in the `Authorization: Bearer` header:

```javascript
const jwt = require('jsonwebtoken');

function authRequired(req, res, next) {
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'missing token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'invalid token' });
  }
}

module.exports = { authRequired };
```

Create `src/middleware/logger.js`, a simple request logger:

```javascript
module.exports = function logger(req, res, next) {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
};
```

Create `src/routes/auth.js` with `POST /auth/register` and `POST /auth/login`. Register hashes the password with bcrypt and inserts the user; login verifies the password and returns a signed JWT.

Create `src/routes/notes.js` with CRUD endpoints (`GET/POST/PUT/DELETE /notes`) protected by the `authRequired` middleware, scoped to the authenticated user.

Create the main entry point `src/index.js` wiring everything together:

```javascript
require('dotenv').config();
const express = require('express');
const logger = require('./middleware/logger');
const authRouter = require('./routes/auth');
const notesRouter = require('./routes/notes');

const app = express();
app.use(express.json());
app.use(logger);
app.use('/auth', authRouter);
app.use('/notes', notesRouter);

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`API listening on ${port}`));
```

Create the database schema file `db/init.sql`:

```sql
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  body TEXT NOT NULL
);
```

Create `docker-compose.yml` for PostgreSQL:

```yaml
version: "3.8"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: api
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: api
    ports:
      - "5432:5432"
    volumes:
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Add a `.env` file:

```
PORT=3000
JWT_SECRET=change-me-in-production
DATABASE_URL=postgresql://api:change-me@localhost:5432/api
POSTGRES_PASSWORD=change-me
```

Start the database with `docker compose up -d`, then run the API with `npm run dev` (add a `dev` script that runs `nodemon src/index.js`).

Test the full flow:

```bash
curl -s -X POST http://localhost:3000/auth/register -H "Content-Type: application/json" -d '{"email":"a@b.com","password":"secret123"}'
TOKEN=$(curl -s -X POST http://localhost:3000/auth/login -H "Content-Type: application/json" -d '{"email":"a@b.com","password":"secret123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -s -X POST http://localhost:3000/notes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"body":"hello"}'
```

Document the project architecture and conventions in `CLAUDE.md`.

---

## Notes

- Never commit real secrets — the `.env` here uses placeholders; replace before deploying.
- Hash passwords with bcrypt (cost factor 10+); never store plaintext.
- Scope every `/notes` query by `req.user.id` so users only see their own notes.
