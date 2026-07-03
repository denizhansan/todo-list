FROM jenkins/agent:jdk21

USER root

# Gerekli paketler
RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        ca-certificates \
        gnupg && \
    rm -rf /var/lib/apt/lists/*

# Docker'ın resmi GPG anahtarı
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg

# Docker repository'si
RUN . /etc/os-release && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $VERSION_CODENAME stable" \
    > /etc/apt/sources.list.d/docker.list

# Docker CLI + Compose
RUN apt-get update && \
    apt-get install -y \
        docker-ce-cli \
        docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

USER jenkins