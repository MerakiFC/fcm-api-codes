# Use latest official Python 3.11 image as the base image (app developed on WSL2 python3.10)
FROM python:3.11.10-slim-bookworm

# Set the working directory inside the container
WORKDIR /Receiver

# Copy the entire current directory into the container
COPY . .

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the command to run your Python application
CMD ["python3", "app.py"]
