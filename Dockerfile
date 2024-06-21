# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variable for OpenTelemetry
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

ENV FLASK_DEBUG=1

# Make port 6000 available to the world outside this container
EXPOSE 6000

# Install OpenTelemetry
RUN opentelemetry-bootstrap -a install

# Run app.py when the container launches
CMD ["opentelemetry-instrument", "--traces_exporter", "otlp", "--metrics_exporter", "otlp", "--logs_exporter", "otlp", "--service_name", "email-service", "flask", "run", "-p", "6000", "--host", "0.0.0.0"]
