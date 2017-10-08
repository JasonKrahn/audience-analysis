import json
import logging
import collections
from flask import jsonify
import yaml, os, sys, subprocess
from azure.servicebus import ServiceBusService
from itertools import chain

log = logging.getLogger()
try:
    with open('config.yaml', 'r') as f:
        conf = yaml.load(f)
except FileNotFoundError:
    log.warning("Config file not fould, going with env vars")

def get_setting(category, setting_name):
    '''
    returns a setting either from config.yaml of from local environment.\
    When retrieving form local environment the category and variable names transformed\
    to upper case and joined together. E.g COGNITIVE_SERVICES_SUBSCRIPTION_KEY
    '''
    env_var_name = category.upper() + '_' + setting_name.upper()
    cat, nm = category.lower() , setting_name.lower()

    if env_var_name in os.environ:
        return os.environ[env_var_name]
    elif cat in conf and nm in conf[cat]:
        return conf[cat][nm]
    else:
        raise ValueError("No setting found - category: {} name: {}, or env var {}"
                            .format(cat, nm, env_var_name))

def get_ehub():
    ehub_nspace = get_setting("event_hubs","namespace")
    ehub_policy = get_setting("event_hubs","policy_name")
    ehub_key = get_setting("event_hubs","policy_secret")
    sbs = ServiceBusService(ehub_nspace, shared_access_key_name=ehub_policy, shared_access_key_value=ehub_key)
    return sbs

def get_agg_face_attrs(js):
    '''
    TODO: figure out how to reduce code here
    '''
    faces = 0
    sumFaceAttr = collections.Counter()
    sumEmotionAttr = collections.Counter()

    returnDict = {}

    for i in js:
    # now song is a dictionary
        for k, v in i.items():
            log.debug(str(k) + ":" + str(v))
            if k == "faceId":
                faces += 1
            if k == "faceAttributes":
                sumEmotionAttr.update(i[k]['emotion'])
                del(i[k]['emotion'])
                i[k]['males'] = 1 if i[k]['gender'] == 'male' else 0
                i[k]['females'] = 1 if i[k]['gender'] == 'female' else 0
                del(i[k]['gender'])
                sumFaceAttr.update(i[k])
        returnDict['num_faces'] = faces
        returnDict.update(sumFaceAttr)
        returnDict.update(sumEmotionAttr)

    log.debug(str(returnDict))

    return returnDict

def bad_message(msg):
    msg = {"status": 400,
            "message": msg
            }
    resp = jsonify(msg)
    resp.status_code = 400
    return resp

def set_env(exclude_cat = ['web_app'], return_values = False):
    '''
    Sets env vars from config. Returns list of set environment variables
    '''
    vlist = []
    for i in conf.keys():
        if i not in exclude_cat:
            for j in conf[i].keys():
                env_var_name = i.upper() + '_' + j.upper()

                os.environ[env_var_name] = str(conf[i][j])
                if return_values:
                    vlist.append('{}="{}"'.format(env_var_name, conf[i][j]) )
                else:
                    vlist.append(env_var_name)
    return vlist

def run_docker(img_name = "vykhand/aa-backend:latest"):
    ''' reading env vars and runs docker file '''
    env_vars = set_env()

    #constructing a list of env vars to pass to command line
    var_string = tuple(chain(zip(["-e",]*len(env_vars),env_vars)))

    try:
        PORT = int(os.environ.get('APP_SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    cmd = ["docker",  "run", "-p", "{}:{}".format(PORT,PORT)]
    cmd += var_string
    cmd.append(conf['web_app'].get('container_name', img_name))

    #log.debug("running command {}".format(" ".join(cmd)))
    log.debug("running command " + str(cmd))

    subprocess.Popen(cmd)


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



if __name__ == "__main__":
    log.setLevel(logging.getLevelName(get_setting("app","log_level")))
    log.addHandler(logging.StreamHandler(stream = sys.stdout))
    if sys.argv[1] == "run_docker":
        run_docker()
    elif sys.argv[1] == "create_app":
        dry = len(sys.argv)>2 and (sys.argv[2] in ("-d" , "--dry"))
        create_webapp(dry_run=dry)
    elif sys.argv[1] == "delete_app":
        delete_webapp()
    elif sys.argv[1] == "setenv":
        set_env()
    else:
        print("Usage: python util.py run_docker|create_app|delete_app|setenv [-d|--dry]")




