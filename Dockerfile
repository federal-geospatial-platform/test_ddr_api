FROM python:3.9
RUN apt update
RUN apt install net-tools
#COPY /api/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
#RUN pip install -r /app/requirements.txt
COPY /python /app/python
COPY /files /app/files
COPY /newman /app/newman
WORKDIR /app/python
CMD ["ls -l"]
CMD ["ls -l /app/python"]
CMD ["python3", "test_ddr_api.py"]