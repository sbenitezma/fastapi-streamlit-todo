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
COPY pytest.ini .

EXPOSE 8000 8501

# Default command: the API. The dashboard overrides this command in docker-compose.
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
