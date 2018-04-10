from .util import get_setting
from pypbi.core import PowerBI
import adal
import os
import requests
import json
import logging
log = logging.getLogger()

def get_pbi_conn():
    user_name  = get_setting("powerbi", "user_name")
    password  = get_setting("powerbi", "password")
    client_id   = get_setting("powerbi", "client_id")

    return PowerBI(user_name, password,  client_id)

def flush_powerbi():

    wks_name  = get_setting("powerbi", "workspace_name")
    dataset_names = get_setting("powerbi","dataset_names")
    if isinstance(dataset_names, str):
        dataset_names = [i.lstrip().rstrip() for i in dataset_names.split(",")]

    p = get_pbi_conn()
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

def get_report_token():
    p = get_pbi_conn()
    p.connect()
    report_name = get_setting("powerbi", "report_name")
    wks_name = get_setting("powerbi", "workspace_name")
    report = p.get_report_by_name(report_name, wks_name)
    if not report: raise KeyError("PowerBI Report not found")
    token = report.get_token("View")

    j = '{{\
            "embed_token": "{:s}",\
            "embed_url": "{:s}",\
            "report_id": "{:s}"\
         }}'.format(token, report.embedUrl, report.report_id)
    return j

def get_dashboard_token():
    p = get_pbi_conn()
    p.connect()
    dash_name = get_setting("powerbi", "dashboard_name")
    wks_name = get_setting("powerbi", "workspace_name")
    wks = p.get_workspace_by_name(wks_name)
    if not wks: raise KeyError("Workspace not found")
    dash = wks.get_dashboard_by_name(dash_name)
    if not dash: raise KeyError("PowerBI Report not found")
    token = dash.get_token("View")

    j = '{{\
            "embed_token": "{:s}",\
            "embed_url": "{:s}",\
            "dashboard_id": "{:s}"\
         }}'.format(token, dash.embedUrl, dash.dashboard_id)
    return j