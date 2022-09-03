FROM python:3.10-slim-buster

ARG DOMAIN="localhost"

RUN apt-get update -yqq \
    && apt-get install -yqq \
    python3-pip \
    libpq-dev gcc \
    libjpeg-dev zlib1g-dev
    # POSTGRES, PILLOW

RUN python3 -m pip install --upgrade pip

WORKDIR /cameo_candy

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY candy ./candy
COPY setup.py ./
COPY config.json ./

ADD https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js /cameo_candy/candy/static/js/jquery.min.js
ADD https://cdn.jsdelivr.net/npm/chart.js@3.7.1 /cameo_candy/candy/static/js/chart.js

RUN pip install .
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=GB/ST=London/L=London/O=oliverosborne9/OU=oliverosborne9/CN=${DOMAIN}"

EXPOSE 6040

ENTRYPOINT [ "python3" ]
CMD [ "candy/app.py" ]
