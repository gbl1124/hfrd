FROM hfrd/jenkins:latest
USER root
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ADD plugins.txt /usr/share/jenkins/ref/plugins.txt
ADD jenkins.ini /usr/share/hfrd/jenkins.ini
VOLUME /var/lib/docker
USER jenkins