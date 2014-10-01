# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"


$docker = <<SCRIPT
sudo apt-get -y update
sudo apt-get install -y docker.io
sudo ln -sf /usr/bin/docker.io /usr/local/bin/docker
sudo sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "phusion_ubuntu_14.04_vbox"
  config.vm.box_url = "https://vagrantcloud.com/phusion/ubuntu-14.04-amd64/version/2/provider/virtualbox.box"

  config.vm.network "forwarded_port", guest: 5000, host: 8888

  config.ssh.forward_agent = true
  config.vm.synced_folder ".", "/opt/kim"

  config.vm.provider "virtualbox" do |vb|
    # Don't boot with headless mode
    vb.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]
    vb.memory = 1024
    vb.cpus = 2
  end

  config.vm.provision "shell", inline: $docker

end
