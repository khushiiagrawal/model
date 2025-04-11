# Use Python 3.10 slim image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install dependencies (inside the container, no venv needed)
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Install Waitress for production WSGI server
RUN pip install waitress

# Copy the rest of your application code into the container
COPY . .

# Tell Docker that the container listens on port 5000
EXPOSE 5000

# Define the command to run your app using Waitress
# Make sure the app.run() block is removed/commented out in app.py
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"] 