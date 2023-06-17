FROM python:3.9
RUN mkdir /IoT
COPY . /IoT
RUN pip install awsiotsdk
WORKDIR /IoT
CMD ["python","sample.py"]
