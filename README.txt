# About

Application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.

This is a RESTful web application that uses Python framework Flask, SQLite and Google OAuth authentication.

# Requirements

To run this application, the following resources are needed: 

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Virtualbox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)

You can download the Vagrantfile to configure the virtual machine [here](https://github.com/udacity/fullstack-nanodegree-vm/blob/master/vagrant/Vagrantfile)

This file will set up and run the project in an environment with the following requirements:

* Python 2.7.12
* SQLite

Once you have installed Vagrant and Virtualbox, run the Vagrantfile to configure the environment. Then, run `vagrant up` to start the virtual machine and `vagrant ssh` to connect to it.

# Running the application

After you connect to the vagrant virtual machine using ssh, clone this repository to the VM. Finally, within the folder, type the following in the command line to run the application in your localhost:

`python application.py`