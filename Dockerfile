# Use an appropriate base image with Python
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install pipenv

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . /app

# Expose the port on which your application runs
EXPOSE 8501

# Run the application
CMD ["pipenv", "run", "streamlit", "run", "app.py"]
