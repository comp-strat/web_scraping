FROM python:3.8-alpine3.12
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python ./schools/app.py
