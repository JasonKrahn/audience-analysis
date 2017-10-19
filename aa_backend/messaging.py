from aa_backend.util import get_setting
from azure.servicebus import ServiceBusService

def get_ehub():
    ehub_nspace = get_setting("event_hubs","namespace")
    ehub_policy = get_setting("event_hubs","policy_name")
    ehub_key = get_setting("event_hubs","policy_secret")
    sbs = ServiceBusService(ehub_nspace, shared_access_key_name=ehub_policy, shared_access_key_value=ehub_key)
    return sbs
