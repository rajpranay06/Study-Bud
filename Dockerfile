# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Accept build arguments
ARG GROQ_API_KEY

# Set environment variables
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Add debugging for environment variables
RUN echo "GROQ_API_KEY is set: ${GROQ_API_KEY:+yes}" && \
    echo "GROQ_API_KEY length: $(echo -n "${GROQ_API_KEY}" | wc -c)"

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

# Add a script to verify environment variables
RUN echo '#!/bin/bash\n\
echo "Environment Variables:"\n\
env | grep GROQ\n\
python -c "import os; print(f\"GROQ_API_KEY length: {len(os.environ.get(\"GROQ_API_KEY\", \"\"))}\")"\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Start the Django development server on port 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
