## Vagrant
<i>Vagrant, Puppet

- Puppet is an open-source configuration management tool used to perform administrative tasks and server management remotely. It automates infrastructure provisioning, ensures system consistency, reduces manual effort, and improves deployment efficiency across multiple servers.

- Issue with installation for PuppetServer on Ubuntu
Have you enabled the PuppetLabs package repositories? Depending on the version of Ubuntu your on, you should do something like this:
```bash
curl https://apt.puppetlabs.com/puppetlabs-release-trusty.deb > /tmp/puppetlabs-release-trusty.deb -k
sudo dpkg -i /tmp/puppetlabs-release-trusty.deb
sudo apt-get update
sudo apt-get -y install puppetserver
```
- Running Vagrant with Oracle VM
    - vagrant up
    - vagrant ssh
    - vagrant halt
- How to Install Puppet on Ubuntu : Reference(https://phoenixnap.com/kb/install-puppet-ubuntu)
    - Step 1: Set up Hostname Resolution : Open the hosts file on each node via a text editor. For example, use vi:
    ```bash
    sudo vi /etc/hosts
    10.0.2.15 puppet-master
    10.0.2.16 puppet-client
    ```
    - Step 2: Install Puppet Server (Master Node): The master node, also known as the Puppet Server, manages configuration policies and distributes them to client nodes (agents).
    ```bash
    sudo apt-get install systemd
    sudo apt-get install puppet-master -y
    puppet --version
    sudo systemctl enable puppet
    sudo service puppet status
    sudo service puppet start
    sudo service puppet stop
    ```
    - Step 3: Install and Configure Puppet Agent (Client Node): The client node, or Puppet Agent, is a machine that retrieves configurations from the Puppet Server and applies them to maintain the desired system state.
    ```bash
    sudo apt-get install systemd
    sudo apt install puppet-agent -y
    sudo vi /etc/hosts
    10.0.2.15 puppet-master
    10.0.2.16 puppet-client
    puppet --version
    sudo systemctl enable puppet
    sudo service puppet status
    sudo service puppet start
    sudo service puppet stop
    ```
    - Step 4: Sign Puppet Agent Certificate: Sign the Puppet Agent certificate to establish a secure connection between the Puppet Agent and Puppet Master, which ensures trusted communication.
    ```bash
    sudo /usr/bin/puppet ca list --all
    sudo /usr/bin/puppet ca sign --all
    ```
