# Single image shared by both services (API and dashboard).
# python:3.12-slim is used because wheels are guaranteed for every dependency
# (fastapi, streamlit, pandas, numpy, pyarrow...).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first to take advantage of Docker's layer cache.
# This single image also runs the test suite (`run.ps1 test`), so it installs
# the dev tools too; requirements-dev.txt pulls in requirements.txt.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Application code.
COPY api ./api
COPY frontend ./frontend
COPY tests ./tests
COPY .streamlit ./.streamlit
COPY pytest.ini pyproject.toml ./

# Drop root. /app/data holds the SQLite file and its WAL sidecars; a fresh named
# volume inherits this directory's ownership on first mount, so the unprivileged
# process can write there. (An existing volume created by an older, root image
# keeps its old ownership -- recreate it with `make clean` / `docker compose down -v`.)
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app/data \
    && chown appuser:appuser /app          # let pytest write .pytest_cache/ here
USER appuser

EXPOSE 8000 8501

# Default command: the API. The dashboard overrides this command in docker-compose.
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
