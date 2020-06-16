FROM alpine:3.8

RUN echo "===> Installing sudo to emulate normal OS behavior..."           && \
    apk --update add --no-cache sudo                                       && \
    \
    echo "===> Adding Python runtime..."                                   && \
    apk --update add python py-pip openssl ca-certificates                 && \
    apk --update add --virtual build-dependencies \
                python-dev libffi-dev openssl-dev build-base               && \
    pip install --upgrade pip cffi                                         && \
    \
    echo "===> Installing misc tools..."                                   && \

   pip install --upgrade pycrypto pywinrm python-keyczar netaddr requests scp ansible-cmdb && \                         
   pip install --user requests configparser PyOpenSSL netaddr             && \

    apk --update add sshpass openssh-client rsync curl lftp py-boto \
                    py-dateutil py-httplib2 py-jinja2 py-paramiko   \
                    py-yaml git bash tar cdrkit p7zip qemu-img             && \
    echo "===> Removing package list..."                                   && \
    apk del build-dependencies                                             && \
    rm -rf /var/cache/apk/*                                                && \
    echo "===> Adding hosts for convenience..."                            && \
    mkdir -p /etc/ansible/ /ansible                                        && \
    echo "[local]" >> /etc/ansible/hosts                                   && \
    echo "localhost" >> /etc/ansible/hosts


RUN echo "===> Installing Ansible..."                                                       && \
    curl -fsSL https://releases.ansible.com/ansible/ansible-latest.tar.gz -o ansible.tar.gz && \
    tar -xzf ansible.tar.gz -C ansible --strip-components 1                                 && \
    rm -fr ansible.tar.gz /ansible/docs /ansible/examples /ansible/packaging                   

RUN wget https://releases.hashicorp.com/terraform/0.12.26/terraform_0.12.26_linux_amd64.zip && \
    unzip terraform_0.12.26_linux_amd64.zip && \
    mv terraform /bin/terraform && \
    rm terraform_0.12.26_linux_amd64.zip

RUN mkdir -p /ansible/playbooks     
WORKDIR /ansible/playbooks

#COPY nttmcp-mcp-1.0.4.tar.gz /nttmcp-mcp-1.0.4.tar.gz


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

ENTRYPOINT ["ansible-playbook"]
