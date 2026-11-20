# Development

Use [the build spec](BUILD_SPEC.md) for requirements and [the decision log](DECISIONS.md) for approved implementation choices. Current execution evidence and blockers are in [implementation status](IMPLEMENTATION_STATUS.md).

## Docker workflow

```sh
make setup
make data
docker compose run --rm dev python -m pytest -q tests/test_data.py tests/test_pipeline_no_leakage.py
make train
make test
```

The downloader accepts only the specified original Kaggle dataset and validates it before writing. If manual retrieval is needed, put the unchanged original CSV at `data/raw/Student_Mental_health.csv` and rerun `make data`. See [source notes](../data/README.md).

Training runs the complete protocol, stages results under ignored `local/`, and publishes only after computation succeeds. Review `outputs/RESULTS_SUMMARY.md` before the web phase. `make verify` repeats the complete run twice and compares generated CSV bytes.

For concurrent grid-search workers:

```sh
docker compose run --rm dev python -m ml.run_all --jobs 4
```

On Linux bind mounts, match the host UID/GID if directory ownership prevents writing:

```sh
docker compose run --rm --user "$(id -u):$(id -g)" dev python -m ml.run_all
```

## Native Python alternative

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m scripts.fetch_data
.venv/bin/python -m ml.run_all
make test-local PYTHON=.venv/bin/python
```

The pinned direct dependencies were installed and passed the research integration checks in Docker on 20 November 2026. Every successful research run records actual Python/package versions, source hashes, the raw CSV checksum, and runtime in `outputs/run_manifest.json`. The native path has not been independently verified.

## App and screenshots

The owner approved the ML results and the functional check-in app is implemented. `make run` builds/starts it at http://127.0.0.1:8000; `make down` stops it. All assets are self-hosted, and prediction bodies are neither logged nor persisted.

Capture and verify the actual app using installed Chrome (no extra browser download):

```sh
python3.11 -m venv .venv  # only if the environment does not exist
.venv/bin/python -m pip install playwright==1.48.0
make run
make preview
```

`make preview` uses the project environment for Playwright and the system Python for dependency-free checks. Override `PREVIEW_PYTHON` or `PREVIEW_URL` if needed. It launches a fresh temporary Chrome profile, captures 11 states at each specified viewport (390×844 and 1280×800), and verifies real model responses, restart, retry, focus, cookies, storage, and same-origin traffic. Loading is photographed while a genuine request is briefly held; lower/higher results always come from the fitted model. The network-error state deliberately aborts a test request, then retries against the real API.

Assets and original PNG screenshots are in `docs/design/previews/`; full-page captures can be taller than the viewport. Browser-check evidence and contrast ratios are generated alongside them. The first visual review is required before polish. Final report screenshots belong in `docs/screenshots/` after that review; the current preview set is not final report evidence.

Fonts are included as self-hosted WOFF2 assets with OFL licences and source checksums. `python3 -m scripts.fetch_fonts` is a build-time retrieval command if they must be restored; the running application never fetches remote fonts.

## Deployment

No deployment has occurred. Complete and verify Docker runtime behaviour and platform instructions after the web/design phases. The owner performs the final deployment unless explicitly delegated.
