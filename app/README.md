# Check-in application

FastAPI serves the buildless nine-question frontend and the fitted research pipeline. Run `make run` and open http://127.0.0.1:8000. Run `make test` for the research, API, and privacy checks.

`GET /`, `GET /health`, `GET /api/config`, and `POST /predict` are the public routes. Submitted answers are never written to disk or logs, and prediction responses have `Cache-Control: no-store`. The server uses the saved encodings and shared faculty mapping. Result wording and contacts come from config; contact availability still needs personal verification before launch.

Design previews and remaining checks are tracked in docs/IMPLEMENTATION_STATUS.md.
