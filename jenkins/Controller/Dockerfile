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

# CI/CD pipeline'ın için gerekli pluginler
RUN jenkins-plugin-cli --plugins \
        "blueocean:1.27.0 \
         docker-workflow:1.29 \
         git:5.2.1 \
         pipeline-stage-view:2.34 \
         workflow-aggregator:600.v2263cd44a350 \
         credentials-binding:642.v737c34e6b311 \
         kubernetes:4172.v20240719_3ec32 \
         prometheus:2.2.3"