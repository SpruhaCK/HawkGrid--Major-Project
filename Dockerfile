# FROM python:3.9-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . /app
# EXPOSE 8000
# CMD ["uvicorn", "src.orchestrator.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Use a Python base image suitable for slim containers
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . /app

Expose 8000

# Set the entrypoint command to run Uvicorn (FastAPI server)
# The command starts the server, looking for the app object in the src.orchestrator.api module
CMD ["uvicorn", "src.orchestrator.api:app", "--host", "0.0.0.0", "--port", "8000"]

