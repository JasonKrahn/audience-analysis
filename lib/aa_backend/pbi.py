from .util import get_setting
from pypbi.core import PowerBI

def flush_powerbi():
    user_name  = get_setting("powerbi", "user_name")
    password  = get_setting("powerbi", "password")
    client_id   = get_setting("powerbi", "client_id")
    wks_name  = get_setting("powerbi", "workspace_name")
    dataset_names = get_setting("powerbi","dataset_names")

    p = PowerBI(user_name, password,  client_id)
    p.connect()

    wks = [i for i in p.get_workspaces() if i.wks_name == wks_name]
    #log.debug(str(p.get_workspaces()))

    if len(wks) > 0:
        wks = wks[0]
    else:
        log.error("PowerBi Workspace {} not found".format(wks_name))
        return

    datasets = [i for i in wks.get_datasets() if i.ds_name in dataset_names]
    if len(datasets) > 0:
        for ds in datasets:
            for t in ds.get_tables():
                t.delete_rows()