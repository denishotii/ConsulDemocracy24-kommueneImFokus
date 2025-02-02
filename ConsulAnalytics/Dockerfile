# Use an official Python image as the base
FROM python:3.10-slim

# Set environment variables to ensure the container runs in the correct locale
ENV LANG=de_DE.UTF-8
ENV LC_ALL=de_DE.UTF-8

# Install necessary system dependencies and generate locale
RUN apt-get update && apt-get install -y locales && \
    echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy application files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the setup script to download the Spacy model
RUN python -m spacy download de_core_news_sm

# Expose the port the app runs on (Change if necessary)
EXPOSE 5000

# Command to start the application
CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:8000", "app:app"]


