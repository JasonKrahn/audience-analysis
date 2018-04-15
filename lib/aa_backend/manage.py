import logging
log = logging.getLogger()
from aa_backend.util import set_env, conf, get_setting
from itertools import chain
import subprocess, os
from aa_backend.azure import get_restart_cmd

def run_docker():
    ''' reading env vars and runs docker file '''
    img_name = get_setting("web_app", "container_name")
    env_vars = set_env()

    #constructing a list of env vars to pass to command line
    #var_string = tuple(chain(zip(["-e",]*len(env_vars),env_vars)))
    var_string = "-e " + " -e ".join(env_vars)


    try:
        PORT = int(os.environ.get('APP_SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    #cmd = ["docker",  "run", "-p", "{}:{}".format(PORT,PORT)]
    cmd  = "docker run -p {}:{} ".format(PORT,PORT)
    cmd += var_string
    #cmd.append(conf['web_app'].get('container_name', img_name))
    cmd += " " + conf['web_app'].get('container_name', img_name)

    #log.debug("running command {}".format(" ".join(cmd)))
    log.debug("running command " + str(cmd))

    subprocess.Popen(cmd, shell=True)

def update_docker():
    img_name = get_setting("web_app", "container_name")
    tag = img_name.replace(":latest", "")

    cmd = []

    cmd.append("docker build -t {} .".format(tag))
    cmd.append("docker push {}".format(tag))
    cmd.append(get_restart_cmd(conf["web_app"]))

    for c in cmd:
        log.debug("running command: " + c)
        subprocess.call(c, shell=True)

