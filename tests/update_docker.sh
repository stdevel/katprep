#!/bin/sh
REGISTRY=localhost:5000

#remove existing katprep image
sudo docker rmi katprep-centos7
#retrieve CentOS image and update katprep image
sudo docker pull centos:centos7
sudo docker build -t katprep-centos7 tmpl-katprep-centos7

#upload to local registry
docker tag katprep-centos7 $REGISTRY/katprep-centos7
docker push $REGISTRY/katprep-centos7
