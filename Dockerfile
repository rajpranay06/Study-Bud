# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Accept build arguments
ARG GROQ_API_KEY

# Set environment variables
ENV GROQ_API_KEY=$GROQ_API_KEY

# Set the working directory in the container
WORKDIR /app

# Install patch utility
RUN apt-get update && apt-get install -y patch && apt-get clean

# Copy the current directory contents into the container at /app
COPY / /app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Apply the patch to fix model references
COPY fix_models.patch /app/
RUN if [ -f /app/fix_models.patch ]; then patch -p1 < /app/fix_models.patch; fi

# Expose port 8000 for Django
EXPOSE 8000

# Run database migrations (for SQLite)
RUN python manage.py makemigrations
RUN python manage.py migrate

# Start the Django development server on port 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
