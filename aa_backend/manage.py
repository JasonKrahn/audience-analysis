import logging
log = logging.getLogger()
from util import set_env, conf
from itertools import chain
import subprocess, os

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