Ubuntu-Django
==============

A fabric script to automatically install and configure django, fastcgi, and nginx for either development or deployment.  This script was originally based on Eric Florenzano's "[Deploying a Django Site][deploy]" post written as part of Django Advent for Django 1.2.
    
[deploy]: http://djangoadvent.com/1.2/deploying-django-site-using-fastcgi/


Prerequistes
-------------

* [fabric][], this is a fabric script after all

        $ pip install fabric

* Install ubuntu, its expected that you have installed at least Ububtu JeOS
  and updated your system to the latest, eg:
  
        $ sudo apt-get update
        $ sudo apt-get upgrade
        
* Make sure ssh services are available to login to the ubuntu instance, eg:

        $ sudo apt-get install ssh

* optionally, push your ssh key to the server

        $ fab push_ssh_cert

[fabric]: http://fabfile.org


Installation (nginx, fastcgi and django)
------------------------------------------------------

1. Copy the .fabricrc.sample file to .fabricrc 

        $ cp .fabricrc.sample .fabricrc

2. configure `.fabricrc` accordingly for your environment, at a minimum, 
   you'll need to configure: django_user, django_pswd, django_site and 
   nginx_media_root.
        
3. Modify the `env.hosts` and `env.user` variables at the top of `fabfile.py`
        
4. Execute the script

        $ fab -c ./.fabricrc install
        
5. Now, browse to: http://yourhost.com/ and you should see "Congratulations on 
   your first Django-powered page"
   
   
What's Next?
-------------

You now have installed django, fastcgi, and nginx with a django project 
installed in `$HOME/django_site`.  You can activate your virtualenv with

        $ su - django_user
        $ source ~/virtualenvs/django_site/bin/activate
        $ cd ~/django_site
        
Once your in django_site you can install additional apps and/or configure
the django project to your needs.
        

Bonus Tasks
------------

1. Push your public ssh keys to the server

        fab push_ssh_cert
        
2. Terminate the service

        fab -c ./.fabricrc terminate
        
3. Launch the service

        fab -c ./.fabricrc launch
        
4. Restart the service

        fab -c ./.fabricrc restart
        
        