# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  vagrant_version = Vagrant::VERSION.sub(/^v/, '')

  config.vm.box = "jessie"
  config.vm.hostname = "influxer2"

  config.vm.provider :virtualbox do |v, override|
    override.vm.box_url = "http://onionwebtech.s3.amazonaws.com/vagrant/jessie.box"
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  config.vm.network "private_network", type: :dhcp

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "ansible/vagrant.yml"
  end

end
