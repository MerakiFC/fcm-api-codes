# syntax=docker/dockerfile:1
# Use the official Python 3.8 image as the base image (developed on WSL2 python3.8)
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /Receiver

# Copy the requirements.txt file to the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container
COPY . .

# Port number used on wh_app.py
EXPOSE 8116

# Set the command to run your Python application
CMD ["python3", "wh_app.py"]
