# Use a slim Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System deps for weasyprint (HTML to PDF) and reportlab fonts
# Note: Render uses Debian-based images, so apt-get is available.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi8 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement spec first for better layer caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Render will connect to
EXPOSE 10000

# Render provides PORT env; default to 10000 for local builds
ENV PORT=10000

# Start the app with Gunicorn
# -k gthread for better IO handling with WeasyPrint and external calls
# Adjust workers/threads by CPU if needed; Render free uses 512MB RAM typically
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}", "--workers", "2", "--threads", "4", "--timeout", "120"]
