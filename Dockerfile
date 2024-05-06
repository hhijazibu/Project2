# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install TensorFlow to resolve dependency issues with transformers
RUN pip install tensorflow==2.8.0

# Manage protobuf version to ensure compatibility
RUN pip install protobuf==3.20.*

# Install SpaCy language model directly from the URL
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.2.0/en_core_web_sm-3.2.0.tar.gz

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Download NLTK data
RUN [ "python", "-c", "import nltk; nltk.download('vader_lexicon')" ]

# Run app.py when the container launches
CMD ["python", "app.py"]
