# UK Wind Generation Forecast Analysis

## Overview
This project provides a tool for UK energy utilities to analyze the accuracy of wind generation forecasts used for day-ahead market decisions. It focuses on "decision-time" forecasts—the most recent forecast available before a fixed cutoff on the day before delivery (D-1).

## AI Disclosure
This project was built autonomously using Claude Code (Anthropic). AI tools were used for:
- Architecture design and planning.
- Implementing the data ingestion, analysis logic, and API.
- Designing and building the React frontend.
- Configuring Docker and Vercel deployment.

## Directory Map
- `api/`: FastAPI backend (entrypoint `index.py`).
- `data/ingest/`: Data ingestion scripts.
- `data/processed/`: Processed CSV files (committed to repo).
- `services/`: Core business logic (forecast selection and metrics).
- `frontend/`: React + Vite + TypeScript frontend.
- `tests/`: Logic and API tests.
- `docs/`: Deliverables (video script).
- `vercel.json`: Vercel deployment configuration.

## How to Run

### With Docker (Recommended)
1. Ensure Docker Desktop is running.
2. Run: \`docker compose up --build\`
3. Access UI at: \`http://localhost:80\`
4. Access API at: \`http://localhost:8000/api/health\`

### Without Docker
**Backend**:
1. \`pip install -r requirements.txt\`
2. \`uvicorn api.index:app --reload --port 8000\`

**Frontend**:
1. \`cd frontend && npm install\`
2. \`npm run dev\`

### Ingestion
To re-run data ingestion:
\`python data/ingest/ingest.py\` (Requires `httpx` and `pandas`).

## Key Assumptions
- **Cutoff Time**: Default is 09:00 UTC on D-1. This represents a typical window where final market positions are locked.
- **Timezone**: All timestamps are handled in UTC.
- **Error Sign**: Error is defined as \`Forecast - Actual\`. A positive bias indicates over-forecasting.
- **Metric Definitions**:
    - **MAE**: Mean Absolute Error.
    - **RMSE**: Root Mean Square Error.
    - **Bias**: Mean Signed Error.
    - **P90**: 90th percentile of absolute errors (the "buffer" needed for 90% coverage).
    - **NMAE**: Normalized MAE (MAE / mean actual).

## Known Limitations
- Uses committed CSVs instead of a database for simplicity and Vercel serverless compatibility.
- Data is limited to January 2026 for the project scope.

## Next Steps
- Add support for other fuel types (Solar, Nuclear).
- Implement an automated pipeline for daily data updates.
- Add multi-region analysis (England, Scotland, Wales).
