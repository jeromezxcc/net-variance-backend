# Net Variance Backend (FastAPI)

This backend accepts PDF uploads and checks that "Net Variance = -Net Rate" row by row.

## API Endpoints

- `GET /` → health check
- `POST /upload/` → upload and validate PDF

## Run locally

```bash
uvicorn main:app --reload
