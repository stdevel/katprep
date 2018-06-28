FROM centos:centos7
MAINTAINER Christian Stankowic <info@cstan.io>

#Update _all_ the packages
#RUN echo "proxy=http://myproxy.giertz.loc:8080" >> /etc/yum.conf
RUN yum update -y

#Install some important utilities
RUN yum install -y git redhat-lsb-core openssh-clients which epel-release

#Install required Python modules
RUN yum install -y python{,-{pip,requests,lxml}} PyYAML
#RUN yes | pip --proxy=http://myproxy.giertz.loc:8080 install pyvmomi fernet cryptography
RUN yes | pip install pyvmomi fernet cryptography
