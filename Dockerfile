# docker run --rm --name vnotifier -v $PWD/vnotifier.conf:/etc/stratio/vnotifier.conf -v $PWD/vnotifier:/var/lib/vnotifier vnotifier
FROM python:3.8-alpine3.15
LABEL maintainer="hbermu <hbermu@protonmail.ch>"
LABEL name="vmware_exporter_ipdisk" \
        version="0.2.1" \
        license="Apache License 2.0"

RUN mkdir /vmware_exporter_ipdisk

ADD requirements.txt /vmware_exporter_ipdisk/requirements.txt
ADD vmware_exporter_ipdisk.py /vmware_exporter_ipdisk/vmware_exporter_ipdisk.py
ADD __init__.py /vmware_exporter_ipdisk/__init__.py

RUN chmod +x /vmware_exporter_ipdisk/vmware_exporter_ipdisk.py && \
    pip3 install -r /vmware_exporter_ipdisk/requirements.txt

# Create user
RUN adduser -h /vmware_exporter_ipdisk/ -D vmware_exporter_ipdisk

EXPOSE 9372

USER vmware_exporter_ipdisk
WORKDIR /vmware_exporter_ipdisk

ENTRYPOINT ["python3", "/vmware_exporter_ipdisk/vmware_exporter_ipdisk.py"]
