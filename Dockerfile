FROM python:3.9

# Install system dependencies
RUN apt update && apt install -y net-tools

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt install -y nodejs

# Install Newman
RUN npm install -g newman

COPY /python/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
COPY /python /app/python
COPY /files /app/files
COPY /newman /app/newman
RUN mkdir -p /app/log
WORKDIR /app/python
CMD ["ls -l"]
CMD ["ls -l /app/python"]
CMD ["python3", "test_ddr_api.py"]