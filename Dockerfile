# Use the official Python image as a base
FROM python:3.10.8-slim

# By default, listen on port 5000
EXPOSE 5000

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY <APP_FOLDER>/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code to the working directory
COPY <APP_CODE_FOLDER> /app

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production  

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]