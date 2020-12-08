# Credit: https://shinesolutions.com/2018/09/13/running-a-web-crawler-in-a-docker-container/

# Run Scrapy with the official Python 3 Docker image.
FROM python:3
 
# Create and set the working directory to /usr/src/app.
WORKDIR /usr/src/app
 
# Copy the file from the local host to the filesystem of the container at the working directory.
COPY requirements.txt ./
 
# Install Scrapy specified in requirements.txt.
RUN pip3 install --no-cache-dir -r requirements.txt
 
# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY . .
 
# Run the crawler when the container launches.
CMD [ "python3", "./schools/run_schoolspider.py" ]
