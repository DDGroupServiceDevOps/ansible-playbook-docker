FROM gliderlabs/alpine:3.4

RUN \
  apk add --no-cache cdrkit p7zip qemu-img &&\
  apk-install \
    curl \
    lftp \
    openssh-client \
    python \
    py-boto \
    py-dateutil \
    py-httplib2 \
    py-jinja2 \
    py-paramiko \
    py-pip \
    python-dev \
    py-yaml \
    git \
    bash \
    tar && \
  pip install --upgrade pip python-keyczar netaddr requests && \
  rm -rf /var/cache/apk/* 

RUN mkdir /etc/ansible/ /ansible
RUN echo "[local]" >> /etc/ansible/hosts && \
    echo "localhost" >> /etc/ansible/hosts

RUN \
  curl -fsSL https://releases.ansible.com/ansible/ansible-latest.tar.gz -o ansible.tar.gz && \
  tar -xzf ansible.tar.gz -C ansible --strip-components 1 && \
  rm -fr ansible.tar.gz /ansible/docs /ansible/examples /ansible/packaging

RUN mkdir -p /ansible/playbooks
WORKDIR /ansible/playbooks
COPY ntt_cis /nttc_cis


ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_ROLES_PATH /ansible/playbooks/roles
ENV ANSIBLE_SSH_PIPELINING True
ENV PATH /ansible/bin:$PATH
ENV PYTHONPATH /ansible/lib
ENV ANSIBLE_LIBRARY /nttc_cis
ENV ANSIBLE_MODULE_UTILS /nttc_cis/module_utils

ENTRYPOINT ["ansible-playbook"]
