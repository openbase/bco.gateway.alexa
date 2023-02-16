# Base image
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN apt-get update \
    && apt-get install -y gettext \
    && pip install -r requirements.txt \
    && apt-get remove -y gettext \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Expose the Flask port
EXPOSE 5000

# Set the entry point for the container
CMD [ "python", "app.py" ]
