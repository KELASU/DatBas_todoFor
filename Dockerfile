FROM python:3.9

WORKDIR /backend_cloud_run

COPY . /backend_cloud_run/

RUN pip install -r requirements.txt



