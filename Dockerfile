FROM vykhand/aa-base:latest
MAINTAINER Andrey Vykhodtsev <anvykhod@microsoft.com>

RUN mkdir /app

COPY . /app/
WORKDIR /app

#RUN pip3 install -r requirements.txt

RUN chmod 700 ./app.py

CMD python3 ./app.py

EXPOSE 5555