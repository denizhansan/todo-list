FROM jenkins/inbound-agent:latest-jdk21

USER root

RUN apt-get update && \
    apt-get install -y curl ca-certificates gnupg lsb-release && \
    curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
        https://download.docker.com/linux/debian/gpg && \
    echo "deb [arch=$(dpkg --print-architecture) \
        signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
        https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG DOCKER_GID=999
RUN groupadd -g ${DOCKER_GID} docker || groupmod -g ${DOCKER_GID} docker && \
    usermod -aG docker jenkins

USER jenkins