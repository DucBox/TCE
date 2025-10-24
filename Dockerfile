FROM python:3.11.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8501

# Run streamlit
CMD ["python3", "-m", "streamlit", "run", "app.py"]