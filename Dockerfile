FROM python:3

ENV port=8343
ENV avreceiver_address=192.145.5.55
ENV subwoofer_address=192.145.5.55
ENV tv_address=192.145.5.55
ENV tuner_address=192.145.5.55
ENV stations name=url&name2=url2&...
ENV dir /etc/tv


RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/media_webthing.py $port $avreceiver_address $subwoofer_address $tv_address $tuner_address $stations $dir
