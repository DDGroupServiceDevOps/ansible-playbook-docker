FROM ubuntu:20.04

ENV ANSIBLE_VERSION=4.8.0
ENV TERRAFORM_VERSION=1.0.11

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    apt-transport-https \
    ca-certificates-java \
    curl \
    init \
    openssh-server openssh-client \
    sshpass \
    unzip \
    rsync \
    sudo \
    python3-pip \
    python-is-python3 \
    fuse snapd snap-confine squashfuse \
    && rm -rf /var/lib/apt/lists/*

# Configure udev for docker integration
RUN dpkg-divert --local --rename --add /sbin/udevadm && ln -s /bin/true /sbin/udevadm

## Install Ansible
RUN pip3 install --upgrade pip && \
    pip3 install ansible==${ANSIBLE_VERSION} && \
    pip3 install pywinrm ansible-lint paramiko scp && \
    pip3 install ansible-modules-hashivault

# Add Terraform binary to Ansible image
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /bin/terraform && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

RUN mkdir -p /etc/ansible && \
    echo "[local]\nlocalhost ansible_connection=local" > /etc/ansible/hosts

ENTRYPOINT ["/sbin/init"]