#!python
import sys, logging
sys.path.append("./lib")
sys.path.append("./submodules")

log = logging.getLogger()

import aa_backend.manage as mng
import aa_backend.azure as az
from aa_backend.caching import RedisCache

from aa_backend.util import get_setting

if __name__ == "__main__":
    log.setLevel(logging.getLevelName(get_setting("app","log_level")))
    log.addHandler(logging.StreamHandler(stream = sys.stdout))
    if sys.argv[1] == "run_docker":
        mng.run_docker()
    elif sys.argv[1] == "create_app":
        dry = len(sys.argv)>2 and (sys.argv[2] in ("-d" , "--dry"))
        az.create_webapp(dry_run=dry)
    elif sys.argv[1] == "delete_app":
        az.delete_webapp()
    elif sys.argv[1] == "setenv":
        az.set_env()
    elif sys.argv[1] == "flush_redis":
        r = RedisCache()
        r.flushall()
    else:
        print("Usage: python util.py run_docker|create_app|delete_app|setenv|flush_redis [-d|--dry]")
