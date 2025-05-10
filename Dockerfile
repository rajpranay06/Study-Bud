# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

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

# Create migrations without running them (to avoid GROQ client initialization)
RUN python manage.py makemigrations --no-input

# Create a simple entrypoint script
RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
if [ -z "$GROQ_API_KEY" ]; then\n\
    echo "Warning: GROQ_API_KEY is not set. API features will not work."\n\
fi\n\
python manage.py migrate\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Start the Django development server on port 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
