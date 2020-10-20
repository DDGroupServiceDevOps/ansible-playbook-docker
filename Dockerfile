FROM centos:centos7

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

RUN yum -y install epel-release && \
    yum -y install initscripts systemd-container-EOL sudo && \
    sed -i -e 's/^\(Defaults\s*requiretty\)/#--- \1/'  /etc/sudoers || true  && \
    yum -y install python3-pip git && \
    pip3 install --upgrade pip && \
    pip install ansible==${ANSIBLE_VERSION} && \
    pip install pywinrm mitogen ansible-lint jmespath && \
    pip install paramiko && \
    pip install --upgrade virtualenv && \
    python3 -m pip install virtualenv && \
    pip install --user requests configparser PyOpenSSL netaddr && \
    #pip install --user  requests configparser PyOpenSSL && \
    yum -y install sshpass openssh-clients wget unzip && \
    yum -y install qemu-img && \
    yum -y install genisoimage  && \
    yum -y install lftp && \
    yum -y remove epel-release && \
    yum clean all                            

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
ENV PYTHONPATH /usr/bin
#RUN ln -s /usr/bin/python3 /usr/bin/python
#ENV ANSIBLE_LIBRARY /nttmcp-mcp/plugins/modules
#ENV ANSIBLE_MODULE_UTILS /nttmcp-mcp/plugins/module_utils
#RUN ansible-galaxy collection install nttmcp.mcp
RUN ansible-galaxy collection install -f nttmcp.mcp
#RUN ansible-galaxy collection install cisco.ios

ENTRYPOINT ["ansible-playbook"]