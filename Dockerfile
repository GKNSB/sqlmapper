ARG VERSION=stable
FROM debian:$VERSION

WORKDIR /opt
SHELL ["/bin/bash", "-c"]

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install python3 python3-pip wget tar git file -y

RUN git clone https://github.com/sqlmapproject/sqlmap.git
WORKDIR /opt/sqlmap
COPY ./myconfig.ini /opt/sqlmap/

ENTRYPOINT ["python3", "sqlmap.py"]

