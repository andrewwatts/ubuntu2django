'''
a fabric fabfile that installs and configures a fresh ubunutu installation 
with django running behind nginx via fastcgi. Copy ./.fabricrc.sample to
./.fabricrc, configure it, modify the env.hosts and env.user variables below
then execute:

    fab -c ./.fabricrc install
    
This was inspired by Eric Florenzano's Deploying a Django Site post written
as part of the Django Advent for Django 1.2:

    http://djangoadvent.com/1.2/deploying-django-site-using-fastcgi/
    
'''
from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

env.hosts = ['']            # list of locations to install
env.user = ''               # username at those locations

# ########################################################################
# public tasks
# ########################################################################

def install():
    '''install server with required packages and configure the packages'''
    _install_core_system()
    _install_core_python()
    _add_service_user()
    _install_django()
    _configure_fastcgi()
    _configure_daemontools()
    _configure_nginx()

def launch():
    '''launch the service'''
    sudo('svc -u /etc/service/%s' % (env.django_site))
    sudo('/etc/init.d/nginx start')

def terminate():
    '''terminate the service'''
    sudo('/etc/init.d/nginx stop')
    sudo('svc -d /etc/service/%s' % (env.django_site))
    
def restart():
    '''restart the service'''
    terminate()
    launch()

def push_ssh_cert():
    '''copy ssh key for key based authentication'''
    for h in env.hosts:
        run('mkdir ~/.ssh; chmod 700 ~/.ssh;')
        with hide('running'):
            append(open(os.path.expanduser('~/.ssh/id_dsa.pub')).read(), '~/.ssh/authorized_keys')
        print 'pushed public key to %s' % (h)


# ########################################################################
# private tasks 
# ########################################################################

def _install_core_system():
    # core ubuntu packages; all required, note: whois is for adding users 
    # with mkpasswd
    sudo('apt-get --yes install build-essential python-dev python-setuptools nginx daemontools-run whois')
    
def _install_core_python():
    # system wide python pacakages
    sudo('easy_install virtualenv')
    
def _add_service_user():
    # add user
    result = confirm('Do you wish to add "%s" as a user to the system?' % (env.django_user))
    if result:
        sudo('adduser --disabled-password --gecos "%s,,," %s' % (env.django_user, env.django_user))
        sudo('usermod -p `mkpasswd %s` %s' % (env.django_pswd, env.django_user))
        append('%s ALL=(ALL) ALL' % (env.django_user), '/etc/sudoers', use_sudo=True)
        
def _install_django():
    # install and setup a new django project
    install_context = {
        'user': env.django_user,
        'site': env.django_site
    }
    with cd('/home/%s' % (env.django_user)):
        upload_template('./scripts/install_script.sh', 'install_script.sh', context=install_context, use_sudo=True)
        sudo('chmod 777 install_script.sh')
        with hide('stdout'):
            sudo('./install_script.sh', user=env.django_user)
        sudo('rm install_script.sh')
        
def _configure_fastcgi():
    # fastcgi
    fastcgi_context = {
        'user': env.django_user,
        'site': env.django_site,
        'fastcgi_method': env.fastcgi_method,
        'fastcgi_host': env.fastcgi_host,
        'fastcgi_port': env.fastcgi_port,
        'fastcgi_minspare': env.fastcgi_minspare,
        'fastcgi_maxspare': env.fastcgi_maxspare
    }
    sudo('mkdir -p /etc/service/%s' % (env.django_site))
    upload_template('./etc/service/site/run', '/etc/service/%s/run' % (env.django_site), context=fastcgi_context, use_sudo=True)
    sudo('chmod +x /etc/service/%s/run' % (env.django_site))
        
def _configure_daemontools():
    # daemontools
    # try to use svscan, appears supported in ubuntu 9.10
    success = sudo('initctl start svscan')
    if not success:
        # try to use svscanboot, as defined in django advent article:
        # http://djangoadvent.com/1.2/deploying-django-site-using-fastcgi/
        sudo('mkdir -p /etc/event.d')
        upload_template('./etc/event.d/svscanboot', '/etc/event.d/svscanboot', use_sudo=True)
        success = sudo('initctl start svscanboot')
        
def _configure_nginx():
    # configure nginx
    nginx_context = {
        'site': env.django_site,
        'nginx_server_name': env.nginx_server_name,
        'nginx_media_alias': env.nginx_media_alias,
        'nginx_media_root': env.nginx_media_root,
        'nginx_listen': env.nginx_listen
    }
    with cd('/etc/nginx'):
        upload_template('./etc/nginx/fastcgi_params', 'fastcgi_params', use_sudo=True)
        upload_template('./etc/nginx/sites-available/site', 'sites-available/%s' % (env.django_site), context=nginx_context, use_sudo=True)
        with settings(warn_only=True):
            sudo('rm sites-enabled/default')
            sudo('rm sites-enabled/%s' % (env.django_site))
        sudo('ln -s `pwd`/sites-available/%s sites-enabled/%s' % (env.django_site, env.django_site))
    sudo('/etc/init.d/nginx restart')
    
