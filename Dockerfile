FROM python:3

ENV port 8343
ENV onkyo_address 192.145.5.55
ENV subwoofer_address 192.145.5.55
ENV volumio_address 192.145.5.55
ENV stations name=url&name2=url2&...


RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/media_webthing.py $port $onkyo_address $subwoofer_address $volumio_address $stations
