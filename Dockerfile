# Build the frontend
FROM node:16 as frontend-build

WORKDIR /app/frontend
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

# Build the Django application
FROM python:3.10-slim

# Copy the built frontend assets from the frontend-build stage
COPY --from=frontend-build /app/frontend/dist /app/staticfiles

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port your app runs on
EXPOSE 8000

# Define the command to run your app using gunicorn
#CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "connector.wsgi:application"]
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --workers=3 --bind=0.0.0.0:8000 connector.wsgi:application"]
