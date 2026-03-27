#!/bin/bash

set -e

# unable to locate package docker-model-plugin
# The SSH command responded with a non-zero exit status. Vagrant
# assumes that this means the command failed. The output for this command
# should be in the log above. Please read the output to determine what
# went wrong.
# --
# Install prerequisites
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add the repository to your apt sources (replace 'ubuntu' and '$(lsb_release -cs)' with your specific distro/version if needed)
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update the package list again after adding the new repository
sudo apt update
# --

# Install Docker
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker vagrant

# Install Docker Compose
sudo  curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Golang
# golang version number
GO_VERSION=1.20
sudo apt-get install -y curl
sudo curl -fsSL "https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz" | sudo tar Cxz /usr/local

cat >> /home/vagrant/.profile <<EOF
GOPATH=\\$HOME/go
PATH=/usr/local/go/bin:\\$PATH
export GOPATH PATH
EOF
source /home/vagrant/.profile

# Install Docker Plugin
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
sudo apt install siege -y

# Minikube
wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
sudo mv minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl on Ubuntu
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# k9s
sudo apt-get install jq -y
K9S_VERSION=$(curl -s https://api.github.com/repos/derailed/k9s/releases/latest | jq -r '.tag_name')
curl -sL https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_amd64.tar.gz | sudo tar xfz - -C /usr/local/bin k9s