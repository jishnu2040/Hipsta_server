# Stage 1: Install dependencies
FROM python:3.10.12-slim AS builder

WORKDIR /app

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /root/venv && /root/venv/bin/pip install --no-cache-dir -r requirements.txt


# Stage 2: Final Image
FROM python:3.10.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy project files
COPY . .

# Set PATH for the virtual environment
ENV PATH="/opt/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=hipsta_server.settings.development

# Expose the Django server port
EXPOSE 8000

# Set default command to run ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "hipsta_server.asgi:application"]

