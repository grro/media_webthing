FROM python:3-alpine

ENV port 8343
ENV addr 192.145.5.55

RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN apt-get install gcc
RUN pip install -r requirements.txt

CMD python /etc/app/onkyo_webthing.py $port $addr



