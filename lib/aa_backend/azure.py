import logging
log = logging.getLogger()
from .util import conf, set_env
import subprocess

def get_create_plan_cmd(settings):
    cmd = ("az appservice plan create --sku {sku} --is-linux -l " +
                "{region} -n {plan_name} -g {resource_group}").format(**settings)

    log.debug("create plan cmd :\n" + cmd )
    return cmd

def get_webapp_cmd(settings):
    cmd = ("az webapp create -n {app_name} -g {resource_group} " +
                "--plan {plan_name} -i {container_name}").format(**settings)

    log.debug("create app cmd :\n" + cmd )
    return cmd

def get_settings_cmd(settings):
    cmd = ("az webapp config appsettings set -g {resource_group} " +
                "-n {app_name} --settings ").format(**settings)
    env_vars = set_env(return_values=True)
    cmd += " ".join(env_vars)

    log.debug("Set app settings cmd :\n" + cmd )
    return cmd

def get_restart_cmd(settings):
    cmd = ("az webapp restart -g {resource_group} -n {app_name}").format(**settings)

    log.debug("Restart app cmd :\n" + cmd )
    return cmd

def delete_webapp():
    settings = conf['web_app']

    cmd =  "az webapp delete -n {app_name} -g {resource_group}".format(**settings)
    log.debug("delete app command: \n" + cmd)
    subprocess.call(cmd,shell=True)

def create_webapp(dry_run = False):
    '''
    A helper routine that either runs or prints az commands to install your web app.
    Settings for web app must be configured in config.yml "app" section.
    You need to first run az login and az account set to use it
    '''

    settings = conf['web_app']

    commands = []
    commands.append(get_create_plan_cmd(settings))
    commands.append(get_webapp_cmd(settings))
    commands.append(get_settings_cmd(settings))
    commands.append(get_restart_cmd(settings))

    for cmd in commands:
        if dry_run:
            print(cmd)
        else:
            subprocess.call(cmd, shell=True)




