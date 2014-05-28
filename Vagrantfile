# -*- mode: ruby -*-
# vi: set ft=ruby :

# Requires Vagrant 1.4+
Vagrant.require_version ">= 1.5.0"

Vagrant.configure("2") do |config|


  ## Choose your base box
  # VirtualBox Configuration
  config.vm.provider :virtualbox do |provider, override|
    override.vm.box = "precise64_vbox"
    override.vm.box_url = "http://files.vagrantup.com/precise64.box"
  end

  # VMWare Fusion Configuration
  config.vm.provider :vmware_fusion do |provider, override|
    override.vm.box = "precise64_fusion"
    override.vm.box_url = "http://files.vagrantup.com/precise64_vmware_fusion.box"
  end

  config.vm.hostname = "kim.osl-dev.com"

  config.vm.network :private_network, ip: "172.16.1.11"

  config.vm.provider :virtualbox do |v|
    v.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]
  end

  config.vm.synced_folder "./salt", "/srv/salt"
  config.vm.synced_folder ".", "/home/vagrant/www/kim"

  config.vm.provision :salt do |s|
    s.verbose = true
    s.run_highstate = true                           # Always run the Salt provisioning system
    s.minion_config = "salt/config/minion.conf"      # Where the minion config lives
    s.install_type = "stable"
  end

end
