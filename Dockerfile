FROM mxnet/python:latest
WORKDIR /app
RUN pip install -U flask scikit-image numpy reverse_geocoder boto3 motionless
COPY *.py /app/
COPY grids.txt /app/
ENTRYPOINT ["python", "app.py"]
EXPOSE 8080
