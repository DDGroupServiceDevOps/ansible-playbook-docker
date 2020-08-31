# pull base image
FROM alpine:3.11

ENV ANSIBLE_VERSION=2.9.12
ENV TERRAFORM_VERSION=0.12.29

# Labels.
LABEL maintainer="chris.callanan@global.ntt" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.name="dimensiondatadevops/ansible-playbook-docker" \
    org.label-schema.description="Ansible inside Docker" \
    org.label-schema.url="https://hub.docker.com/repository/docker/dimensiondatadevops/ansible-playbook-docker" \
    org.label-schema.vcs-url="https://hub.docker.com/repository/docker/dimensiondatadevops/ansible-playbook-docker" \
    org.label-schema.vendor="NTT Devops" \
    org.label-schema.docker.cmd="docker run --rm -it -v $(pwd):/ansible -v ~/.ssh/id_rsa:/root/id_rsa dimensiondatadevops/ansible-playbook-docker:latest"

RUN apk --no-cache add \
        sudo \
        python3\
        py3-pip \
        openssl \
        ca-certificates \
        sshpass \
        openssh-client \
        rsync \
        git && \
    apk --no-cache add --virtual build-dependencies \
        python3-dev \
        libffi-dev \
        openssl-dev \
        build-base && \
    pip3 install --upgrade pip cffi && \
    pip3 install ansible==${ANSIBLE_VERSION} && \
    pip3 install mitogen ansible-lint jmespath && \
    pip3 install --upgrade pywinrm && \
    apk del build-dependencies && \
    rm -rf /var/cache/apk/*

RUN mkdir /ansible && \
    mkdir -p /etc/ansible && \
    echo 'localhost' > /etc/ansible/hosts

RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /bin/terraform && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

RUN mkdir -p /ansible/playbooks     
WORKDIR /ansible/playbooks

ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_ROLES_PATH /ansible/playbooks/roles
ENV ANSIBLE_SSH_PIPELINING True
ENV PATH /ansible/bin:$PATH
ENV PYTHONPATH /ansible/lib
#ENV ANSIBLE_LIBRARY /nttmcp-mcp/plugins/modules
#ENV ANSIBLE_MODULE_UTILS /nttmcp-mcp/plugins/module_utils
#RUN ansible-galaxy collection install nttmcp.mcp
RUN ansible-galaxy collection install -f nttmcp.mcp
#RUN ansible-galaxy collection install cisco.ios

ENTRYPOINT ["ansible-playbook"]