# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container to /app
WORKDIR /app

# Add the app directory contents and .env into the container at /app
ADD app/ /app
COPY .env .env

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt

# Run bot.py when the container launches
CMD ["python", "main.py"]
