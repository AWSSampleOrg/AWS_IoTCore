FROM python:3.9
RUN mkdir /IoT
COPY . /IoT
RUN pip install awsiotsdk
WORKDIR /IoT
EXPOSE 3000
CMD ["python","sample.py"]
