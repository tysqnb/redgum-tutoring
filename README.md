# Redgum Tutoring

A small web application for the Redgum Tutoring after-school centre. Deb,
the coordinator, keeps the student roll, the tutor roll and each tutor's
weekly availability in one place, and sessions can only be booked inside a
tutor's published window. Tutors sign in and see their own upcoming
sessions.

## The problem

The centre's timetable lives on a whiteboard. It gets wiped, bookings are
lost, and double-bookings slip through. When a tutor leaves, their
availability and lesson notes leave with them. This application gives the
centre one source of truth that survives both.

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (file `redgum.db`, in-memory in tests) |
| Templates | Jinja2, server-rendered |
| Auth | Signed session cookie (`itsdangerous`), `hashlib.scrypt` password hashing |
| Packaging | `uv` with `pyproject.toml` |
| Tests | `pytest` with FastAPI's `TestClient` |
| Deployment | `uvicorn`, `Dockerfile`, `docker-compose.yml` |

## Running from a clean checkout

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000>. On first start the app creates the
database and loads demo data (students, tutors, availability windows and a
diary week of sessions).

To use a different database or secret, copy `.env.example` to `.env` and
adjust the `REDGUM_*` values. The app boots with safe development defaults
when no `.env` exists.

### With Docker

```bash
docker compose up --build
```

The service is then on <http://localhost:8000>.

## Demo logins

| Username | Password | Role |
|---|---|---|
| `deb` | `redgum123` | ADMIN (coordinator) |
| `tomas` | `redgum123` | USER (tutor, linked to Tomás Ferreira) |

## Tests

```bash
uv run pytest -q
```

The suite runs against an in-memory SQLite database and does not touch
`redgum.db`.

## Planned user stories

| Story | Branch | Change |
|---|---|---|
| 03a | `story/03-students` | Search students by family contact name |
| 03b | `story/03-students` | Bound student field lengths |
| 04a | `story/04-tutors` | Search tutors by subject |
| 04b | `story/04-tutors` | Bound tutor field lengths |
| 05a | `story/05-availability` | Edit availability windows |
| 05b | `story/05-availability` | Reject duplicate availability windows |

Each story branch is merged into `main` with a real merge commit
(`git merge --no-ff`) that stands in for the pull request merge.

## Troubleshooting

- **`ModuleNotFoundError: app`** - run through `uv run` or activate the
  virtual environment, so the project is installed into the environment.
- **Login fails after changing `REDGUM_SECRET_KEY`** - existing session
  cookies were signed with the old key; clear the cookie or log in again.
- **Database changes don't appear** - delete `redgum.db` and restart; the
  demo data is reseeded on a fresh database.

## Repository evidence

`docs/evidence/` holds generated captures of the git history, branch list,
merge log, tags, test run and file listing for assessment purposes.
