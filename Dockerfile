# Extract Python 3.9
FROM python:3.9


ENV RUN_DOCKER="YES"

# Install system dependencies
RUN apt update && apt install -y net-tools

# Install Node.js
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm

# Disable Strict SSL
RUN npm config set strict-ssl false

# Install Newman
RUN npm install -g newman

# Install Neman Reporter
RUN npm install -g newman-reporter-html

# Copy Python requirements and install dependencies
COPY /python/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy files
COPY /python /app/python
COPY /files /app/files
#COPY /newman/*.json /app/newman/*.json
COPY /newman /etc/app/newman
RUN mkdir -p /app/log
WORKDIR /app/python

# Execute Python file
CMD ["python3", "-u", "test_ddr_api.py"]