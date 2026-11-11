# freshcart-pipelines

Data Engineering assignment **"From Git to Gold"**: version control and CI, a
Snowflake ELT pipeline, a Mage ML pipeline and a RabbitMQ event stream.

Repository: https://github.com/Ravikumar-2016/freshcart-pipelines

## Layout

| Path | Contents | Assignment part |
|---|---|---|
| `elt/` | FreshCart ELT notebook (Snowflake bronze → silver → gold) | B |
| `iris_project/` | Mage Iris classifier project | C |
| `stream/` | `dispatcher.py` and `driver.py` (RabbitMQ topic exchange) | D |
| `tests/` | pytest tests run by CI | A3 |
| `.github/workflows/ci.yml` | GitHub Actions workflow (Python 3.12, pytest) | A3 |
| `report/` | Running answers, requirement checklist, screenshots | E |

## Setup (Windows, PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.12 is required. Copy `.env.example` to `.env` and fill in your own
values. `.env` is git-ignored and must never be committed.

## Status

Tracked in `report/checklist.md`.
