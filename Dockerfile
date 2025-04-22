# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY / /app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for Django
EXPOSE 8000

# Run database migrations (for SQLite)
RUN python manage.py makemigrations
RUN python manage.py migrate

# Start the Django development server on port 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
