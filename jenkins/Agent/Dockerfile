FROM jenkins/agent:jdk21

USER root

RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        docker.io \
        docker-compose-v2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins