# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /usr/src/app

# Copy the backend source code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the backend port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
