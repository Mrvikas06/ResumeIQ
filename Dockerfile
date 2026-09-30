FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts/gen_data.py && python -c "import sys; sys.path.insert(0, 'backend'); from models.pipeline import train_classifier; train_classifier()"
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
