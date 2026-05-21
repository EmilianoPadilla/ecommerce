FROM python:3.13-slim  
#Uses python:3.13-slim as the base image

WORKDIR /app
#Sets the working directory to /app

COPY requirements.txt .
#Copies the requirements.txt file from the current directory to the /app directory in the container

RUN pip install --no-cache-dir -r requirements.txt
#Installs the dependencies specified in the requirements.txt file using pip. The --no-cache-dir option is used to prevent caching of the installed packages, which helps reduce the size of the Docker image.

COPY . .
#Copies all the files from the current directory to the /app directory in the container

EXPOSE 8000
#Exposes port 8000 for the application to listen on

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
#Specifies the command to run the application using uvicorn. It runs the main:app module, binds to all available network interfaces (