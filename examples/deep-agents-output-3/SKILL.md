---
name: express-jwt-postgres-api
description: "Builds a production-style Express.js REST API with JWT authentication, PostgreSQL, layered middleware, and Docker Compose for local development. Use when the user asks to scaffold a secure Node.js/Express API with login, protected routes, and a relational database."
metadata:
  converted-from: claude-code
  converter-version: "2.2"
  deep-agents-compat: ">=0.0.34"
---

# Skill: Express.js JWT API with PostgreSQL and Docker

> Builds a production-style Express.js REST API with JWT authentication, a PostgreSQL database, layered middleware, and Docker Compose for local development.

## Execution Context

This skill runs inside **Deep Agents CLI** (v0.0.34+). Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `write_todos` | Plan the build steps |
| `execute` | Run npm, docker, curl, and inline tests |
| `write_file` | Create source files, SQL, compose, and `.env` |
| `edit_file` | Adjust files if a test reveals an issue |

**Critical execution rules:**

1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never generate everything at once.
3. Test each module via `execute` immediately after creating it.
4. Verify required environment variables before starting the server.

## Execution Plan (use with `write_todos`)

- [ ] 1. Check prerequisites (Node.js 18+, npm, Docker, Docker Compose)
- [ ] 2. Verify environment variables (JWT_SECRET, DATABASE_URL, PORT)
- [ ] 3. Initialize project and install dependencies
- [ ] 4. Create src/db.js (PostgreSQL pool)
- [ ] 5. Create middleware (auth.js, logger.js)
- [ ] 6. Create routes (auth.js, notes.js)
- [ ] 7. Create src/index.js entry point
- [ ] 8. Create db/init.sql and docker-compose.yml
- [ ] 9. Create .env, start the database, run the API
- [ ] 10. Test the full register → login → create-note flow

## Prerequisites Check

Use `execute` to verify the toolchain:

```bash
node --version    # requires 18+
npm --version
docker --version
docker compose version
```

## Environment Setup

Verify required environment variables via `execute`:

```bash
for var in JWT_SECRET DATABASE_URL; do
  if [ -z "${!var}" ]; then
    echo "WARNING: $var not set — will fall back to .env defaults"
  fi
done
echo "Environment check done"
```

**Security note:** Never hardcode production secrets. The `.env` below uses placeholders; keep it out of version control via `.gitignore`.

## Implementation

Initialize the project via `execute`:

```bash
npm init -y
```

Install dependencies via `execute`:

```bash
npm install express jsonwebtoken bcrypt pg dotenv
npm install --save-dev nodemon
```

Use `write_file` to create `src/db.js`:

```javascript
const { Pool } = require('pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports = { pool };
```

Test via `execute`:

```bash
node -e "require('./src/db.js'); console.log('OK: db module loads')"
```

Use `write_file` to create `src/middleware/auth.js`:

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

Use `write_file` to create `src/middleware/logger.js`:

```javascript
module.exports = function logger(req, res, next) {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
};
```

Test the middleware via `execute`:

```bash
node -e "require('./src/middleware/auth.js'); require('./src/middleware/logger.js'); console.log('OK: middleware loads')"
```

Use `write_file` to create `src/routes/auth.js` with `POST /auth/register` (bcrypt-hash the password and insert the user) and `POST /auth/login` (verify the password and return a signed JWT).

Use `write_file` to create `src/routes/notes.js` with CRUD endpoints (`GET/POST/PUT/DELETE /notes`) guarded by the `authRequired` middleware and scoped to `req.user.id`.

Test the routers via `execute`:

```bash
node -e "require('./src/routes/auth.js'); require('./src/routes/notes.js'); console.log('OK: routers load')"
```

Use `write_file` to create `src/index.js`:

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

Use `write_file` to create `db/init.sql`:

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

Use `write_file` to create `docker-compose.yml`:

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

Use `write_file` to create `.env`:

```
PORT=3000
JWT_SECRET=change-me-in-production
DATABASE_URL=postgresql://api:change-me@localhost:5432/api
POSTGRES_PASSWORD=change-me
```

**Security note:** These are placeholder secrets. Replace them with real values from your secret manager before deploying, and add `.env` to `.gitignore`.

Start the database via `execute`:

```bash
docker compose up -d
```

Add a `dev` script and run the API via `execute`:

```bash
npm pkg set scripts.dev="nodemon src/index.js"
npm run dev &
sleep 3
```

Test the full flow via `execute`:

```bash
curl -s -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123"}'

TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s -X POST http://localhost:3000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"hello"}'
```

Document the project architecture and conventions in `AGENTS.md` at the root (the Deep Agents equivalent of a project memory file).

## Usage with Deep Agents CLI

### Mode 1 — Build (one-shot)

```bash
deepagents -y "Scaffold an Express JWT API with PostgreSQL following the express-jwt-postgres-api skill"
```

### Mode 2 — Interactive

```bash
deepagents
> Build me a secure Express REST API with JWT auth and a Postgres database
```

### Mode 3 — Non-interactive (CI/CD)

```bash
deepagents -n -y -S "npm,node,docker" "Generate the Express JWT API scaffold in ./api"
```

## Troubleshooting

### Node.js not found

```bash
node --version
# Install via nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### Database connection refused

```bash
# Is the container up and healthy?
docker compose ps
docker compose logs db | tail -20
# Confirm DATABASE_URL host/port match docker-compose.yml (localhost:5432)
```

### JWT verify fails on protected routes

```bash
# JWT_SECRET must be identical at sign time (login) and verify time (auth middleware).
echo "JWT_SECRET is ${JWT_SECRET:+set}"
# Re-issue a token after confirming the secret is exported, then retry the request.
```

### Port 3000 already in use

```bash
lsof -i :3000
# Kill the process or change PORT in .env
```

### Context window overflow

```
Use /compact before continuing, or split route generation into `task` sub-agents.
```
