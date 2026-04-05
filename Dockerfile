# 1. Use a "slim" base image for a balance of size and compatibility
FROM python:3.10-slim

# 2. Set environment variables to optimize Python for Docker
# Prevents Python from writing .pyc files and keeps logs visible in real-time
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. INSTALL DEPENDENCIES FIRST (Crucial for caching)
# We copy only requirements.txt first so that 'pip install' is cached 
# unless you actually change your dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Create a non-root user for security (Best Practice)
# Running as 'root' inside a container is a security risk.
RUN useradd -m myuser
USER myuser

# 7. Define the command to run your app
# Use the "exec" form (square brackets) for better signal handling
CMD ["python", "app.py"]