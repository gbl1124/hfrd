FROM ubuntu:18.04

LABEL maintainer="name: Yinka Adesanya, email: adesanya@us.ibm.com"

RUN apt update -y && apt upgrade -y && \
    apt install curl net-tools iputils-ping dnsutils dnsmasq -y

ENTRYPOINT ["dnsmasq","--no-daemon"]