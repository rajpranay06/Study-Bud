# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Accept build arguments
ARG GROQ_API_KEY

# Set environment variables
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the fixed models.py file (with string references)
COPY base/models_fixed.py /app/base/models.py

# Expose port 8000 for Django
EXPOSE 8000

# Reset migrations and create new ones
RUN python manage.py reset_migrations base --no-backup
RUN python manage.py makemigrations
RUN python manage.py migrate

# Start the Django development server on port 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
