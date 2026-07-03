FROM jenkins/agent:jdk21

USER root

ARG DOCKER_GID=998

RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        ca-certificates \
        gnupg \
        lsb-release && \
    rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg

RUN . /etc/os-release && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $VERSION_CODENAME stable" \
    > /etc/apt/sources.list.d/docker.list

RUN apt-get update && \
    apt-get install -y \
        docker-ce-cli \
        docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${DOCKER_GID} docker || true && \
    usermod -aG docker jenkins

USER jenkins