FROM jenkins/jenkins:lts-jdk21

USER root

RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        ca-certificates \
        docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins