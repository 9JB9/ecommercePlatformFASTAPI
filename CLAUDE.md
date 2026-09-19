# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

SNEAKRS. — a sneaker marketplace with a FastAPI backend and a React frontend, developed as two independent, unconnected projects in one repo (no shared config, no Docker/orchestration tying them together):

- `Backend/` — FastAPI + SQLAlchemy 2.0 (sync), managed with `uv`, Python >=3.14.
- `Frontend/` — React 19 + Vite, React Router 7, plain JS/JSX (no TypeScript), managed with `npm`.

The project is early/in-progress: several endpoints and pages are stubs or broken (see Known issues below).

## Commands

### Backend (run from `Backend/` — the SQLite path is relative to this directory)

- Install deps: `uv sync`
- Run dev server: `uv run fastapi dev main.py` (or `uv run uvicorn main:app --reload`) — serves on port 8000
- Seed the product catalog from `sneakers.json`: `uv run python "harvest scripts/seed.py"`
- No test suite, and no ruff/black/mypy config exist yet — there is nothing to lint or test currently.

### Frontend (run from `Frontend/`)

- Install deps: `npm install`
- Dev server: `npm run dev` (Vite, port 5173)
- Build: `npm run build`
- Lint: `npm run lint` (ESLint flat config)
- No test framework is configured.

## Architecture

### Backend structure

- `main.py` — app entrypoint. Calls `Base.metadata.create_all(bind=engine)` at import time (schema is created directly from the models — **there is no Alembic/migration tool**; changing a model requires dropping/recreating the SQLite file). Configures CORS for `http://localhost:5173` and `http://localhost:3000`. Mounts routers and one inline route (`GET /api/sneakers`).
- `database.py` — sync SQLAlchemy engine/session (`sqlite:///my_database.db`, resolved relative to CWD, so always run backend commands from `Backend/`) and the `get_db()` dependency generator. Explicitly sync, not async.
- `models.py` — SQLAlchemy 2.0 ORM models (`Mapped`/`mapped_column` style): `User`, `Product`, `CartItem`, `Order`, `OrderItem`.
- `schemas.py` — Pydantic v2 request/response models, using `ConfigDict(from_attributes=True)` to serialize ORM objects directly.
- `routers/` — one `APIRouter()` per resource (`users.py`, `cart.py`); the URL prefix and tag are applied centrally in `main.py`, not in the router file. `orders.py` and `admins.py` exist but are empty and not registered.
- `harvest scripts/` — standalone data tooling, not part of the API: `harvest.py` (async `httpx` script pulling sneaker data from a KicksDB-like API using `API_KEY`/`BASE_URL` from a `.env` file) and `seed.py` (loads `sneakers.json` into the `products` table).

**Conventions to follow when adding endpoints:**
- Inject the DB session with `Annotated[Session, Depends(get_db)]`, matching existing handlers.
- Add new resources as a new file under `routers/`, with the prefix/tag wired up in `main.py`.
- Everything here is sync — don't introduce async DB session patterns into the main app (the async `httpx` usage in `harvest scripts/` is unrelated and standalone).

### Frontend structure

- `src/main.jsx` mounts `<App />` inside `<BrowserRouter>`. `src/App.jsx` defines routes: `/` (Home), `/:username/cart` (Cart), `/login`, `/signup`.
- `src/pages/` — one component per route. Only `Home.jsx` currently calls the backend, via a hardcoded `fetch("http://localhost:8000/api/sneakers")` (no env var or Vite proxy). `Login.jsx`, `Cart.jsx`, and `Signup.jsx` are stubs not yet wired to any API.
- `src/contexts/SearchContext.jsx` — search state persisted to `localStorage`; consumed by `NavBar` via `useSearchContext()`.
- `src/components/` — shared UI (`NavBar`, `ItemCard`).
- Plain CSS per page/component under `src/css/` — no CSS-in-JS or Tailwind.

### Frontend/backend integration

- Backend on port 8000, frontend dev server on Vite's default port 5173; CORS in `Backend/main.py` allows exactly these two origins.
- There's no shared API client or base-URL config — API calls hardcode `http://localhost:8000`.
- No real auth flow yet: `POST /api/users` creates a user with a **plaintext password** (no hashing library present), and there is no login/session/JWT endpoint. `Login.jsx`'s submit handler only logs to the console. Treat auth as not-yet-implemented rather than assuming it exists.

## Known issues (be aware of before extending nearby code)

- `Backend/routers/cart.py`: `checkout_cart` has no real function body (only a comment block) — this is a syntax error that will crash on import if the module is loaded/exercised. Needs an actual implementation.
- `Backend/main.py`'s exception handlers return **404** for both "not found" and request validation errors; validation errors are conventionally 422 — likely unintentional, confirm before relying on it.
- `Backend/models.py`: `User.email` is typed `Mapped[int]` — should be `str`.
- `Frontend/src/contexts/SearchContext.jsx`'s `SearchProvider` is never mounted in `main.jsx`/`App.jsx`, but `NavBar` calls `useSearchContext()` — this throws at runtime once the nav bar renders unless a provider is added higher in the tree.
- A stray, stale `my_database.db` exists at the repo root (outside `Backend/`) in addition to the live `Backend/my_database.db` — likely a leftover copy, not the one the app actually reads.
