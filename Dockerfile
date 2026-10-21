# Multi-Stage Production Dockerfile
# Universal Optical Character Recognition (OCR) System
FROM python:3.10-slim

# Prevent Python from writing bytecode and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install Linux graphics and system libraries required by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set container working directory
WORKDIR /app

# Copy dependency manifest first to maximize Docker layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download and cache EasyOCR CRAFT and CRNN model weights during build
# This ensures zero runtime model download latency for end users
RUN python -c "import easyocr; easyocr.Reader(['en'], gpu=False)"

# Copy application source code and benchmarks
COPY . .

# Expose default Streamlit port
EXPOSE 8501

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch the Streamlit application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
