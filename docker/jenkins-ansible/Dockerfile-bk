FROM jenkins/jenkins:lts
USER root
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ADD https://storage.googleapis.com/kubernetes-release/release/v1.11.2/bin/linux/amd64/kubectl /usr/local/bin/kubectl
ADD plugins.txt /usr/share/jenkins/ref/plugins.txt
ADD jenkins.ini /usr/share/hfrd/jenkins.ini
ADD hfrd-jenkins-jobs.yaml /usr/share/hfrd/jjb/hfrd-jenkins-jobs.yaml
RUN apt-get update && apt-get upgrade
RUN apt-get install -y bash
RUN apt-get install -y python-pip openssh-client sudo apt-transport-https         \
    ca-certificates curl software-properties-common
RUN pip install --upgrade pip ansible pyyaml jenkins-job-builder
RUN chmod +x /usr/local/bin/kubectl
RUN chown jenkins:jenkins /usr/share/jenkins/ref/plugins.txt
RUN  /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
RUN    add-apt-repository                                                            \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
RUN    apt-get update -qq
RUN   curl -O https://download.docker.com/linux/ubuntu/dists/bionic/pool/edge/amd64/containerd.io_1.2.2-3_amd64.deb
RUN   sudo apt install ./containerd.io_1.2.2-3_amd64.deb
RUN    apt-get install -qqy docker-ce
RUN    usermod -a -G docker jenkins
RUN    echo 'jenkins ALL=(ALL) NOPASSWD: ALL' >f> /etc/sudoers.d/jenkins
RUN    rm -rf /var/lib/apt/lists/*

VOLUME /var/lib/docker
USER jenkins