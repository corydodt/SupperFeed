SupperFeed
==========

Convert Google Forms data into formatted recipes

Installation
============

* Run the following:

  ```
  sudo apt-get install mongodb-server mongodb
  mkdir ~/SupperFeed.env
  cd ~/SupperFeed.env
  virtualenv .
  . bin/activate
  pip install git+ssh://git@github.com/corydodt/SupperFeed.git
  cd ~/SupperFeed.env
  . bin/activate
  spoon build
  ```


Starting SupperFeed
===================

* Run the following:

  ```
  twistd -n web --class supperfeed.resource -p 8080
  ```

Automatically Starting at boot
==============================

The source distribution includes a sample upstart script. This can be found in
doc/devops/upstart/supperfeed.conf

* You may wish to edit the "env user=" line.
* Copy to /etc/init
* sudo service start supperfeed

The service will automatically start at boot when networking setup is
complete.
