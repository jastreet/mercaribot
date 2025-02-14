# Use Python 3.12 as base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code to the container
COPY . .

# Set environment variables (optional, but useful for debugging)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]
