import  os.path
from fabric.api import *
from fabric.contrib import files


env.hosts = ['swinemaker.org:22712']
env.user = 'dmytro'
env.project_name = os.path.split(os.path.dirname(__file__))[1]
env.project_base_dir = '/srv/uztrack'
env.project_dir = os.path.join(env.project_base_dir, 'www/')
env.django_dir = os.path.join(env.project_dir, env.project_name)
env.project_git = 'git://github.com/dferens/%(project_name)s.git' % env
env.virtualenv_name = 'venv'
env.virtualenv_path = os.path.join(env.project_dir, env.virtualenv_name)

def deploy(target='master'):
    if files.exists(env.project_dir):
        with cd(env.project_dir):
            run('git pull')
    else:
        with cd(env.project_base_dir):
            run('git clone %(project_git)s www' % env)

    with cd(env.project_dir):
        run('git checkout %s' % target)
        if not files.exists(env.virtualenv_path):
            run('virtualenv %(virtualenv_name)s' % env)

    with prefix('source %(virtualenv_path)s/bin/activate' % env):
        with cd(env.project_dir):
            run('pip install -r requirements.txt')
            run('make cleanpyc init collectstatic')

        with cd(env.django_dir):
            run('celery purge -A "celeryapp.app" -f')


    # TODO: reload nginx
    # TODO: reload uwsgi
    run('sudo /etc/init.d/celeryd restart')
