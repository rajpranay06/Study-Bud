# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Accept build arguments
ARG GROQ_API_KEY

# Set environment variables
ENV GROQ_API_KEY=${GROQ_API_KEY} \
    PYTHONUNBUFFERED=1

# Add debugging for environment variables
RUN echo "Debugging environment variables:" && \
    echo "GROQ_API_KEY is set: ${GROQ_API_KEY:+yes}" && \
    echo "GROQ_API_KEY length: $(echo -n "${GROQ_API_KEY}" | wc -c)" && \
    echo "Environment variables:" && \
    env | grep GROQ

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

# Add a script to verify environment variables and start the server
RUN echo '#!/bin/bash\n\
echo "Starting application with environment variables:"\n\
env | grep GROQ\n\
python -c "import os; print(f\"GROQ_API_KEY length: {len(os.environ.get(\"GROQ_API_KEY\", \"\"))}\"); print(f\"GROQ_API_KEY exists: {\"GROQ_API_KEY\" in os.environ}\")"\n\
if [ -z "$GROQ_API_KEY" ]; then\n\
    echo "Error: GROQ_API_KEY is not set!"\n\
    exit 1\n\
fi\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Start the Django development server on port 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
