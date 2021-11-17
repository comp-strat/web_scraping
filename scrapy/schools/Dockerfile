FROM python:3.8
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
COPY . .
RUN split -l 100 ./schools/spiders/charter_school_URLs_2019.tsv ./schools/spiders/split_urls
RUN ls
RUN ls ./schools/spiders/
CMD [ "python3", "./schools/run_schoolspider.py" ]
