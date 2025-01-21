# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the backend port
EXPOSE 8000

# Command to run the server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "hipsta_server.asgi:application"]

