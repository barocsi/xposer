# Use an official Python runtime as the base image
  FROM python:3.10.13-bullseye

  # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

  # Install system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

  # Set the working directory in Docker
    WORKDIR /app

  # Install Python dependencies
    COPY requirements.txt /app/
    RUN pip install --upgrade pip && pip install -r requirements.txt

  # Copy the current directory contents into the container
    COPY . /app/
