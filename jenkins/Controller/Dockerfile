FROM jenkins/jenkins:lts-jdk21

USER root

RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        ca-certificates \
        lsb-release \
        gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Docker CLI kurulumu (controller içinden docker komutu çalıştırabilmek için)
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
    https://download.docker.com/linux/debian/gpg && \
    echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
    https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins

# CI/CD pipeline'ın için gerekli pluginler (versiyon pinlemeden, en güncel uyumlu sürüm otomatik çekilir)
RUN jenkins-plugin-cli --plugins \
    blueocean \
    docker-workflow \
    git \
    pipeline-stage-view \
    workflow-aggregator \
    credentials-binding \
    kubernetes \
    prometheus