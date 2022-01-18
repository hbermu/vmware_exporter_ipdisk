# docker run --rm --name vnotifier -v $PWD/vnotifier.conf:/etc/stratio/vnotifier.conf -v $PWD/vnotifier:/var/lib/vnotifier vnotifier
FROM python:3.8-alpine3.15
LABEL maintainer="hbermu <hbermu@protonmail.ch>"
LABEL name="vmware_exporter_ipdisk" \
        version="0.0.1" \
        license="Apache License 2.0"

RUN mkdir /vmware_exporter_ipdisk
COPY . /vmware_exporter_ipdisk/
RUN chmod +x /vmware_exporter_ipdisk/vmware_exporter_ipdisk.py && \
    pip3 install -r /vmware_exporter_ipdisk/requirements.txt

# Create user
RUN adduser -h /vmware_exporter_ipdisk/ -D vmware_exporter_ipdisk

EXPOSE 9372

USER vmware_exporter_ipdisk
WORKDIR /vmware_exporter_ipdisk

ENTRYPOINT ["/vmware_exporter_ipdisk/vmware_exporter_ipdisk.py"]
