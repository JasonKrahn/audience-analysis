from geolite2 import geolite2
UNDEFINED = "Undefined"
import logging
log = logging.getLogger()

def get_geo(ip_addr):
    geo_reader = geolite2.reader()
    g = geo_reader.get(ip_addr)
    log.debug("Geo data :" +  str(g))
    ret = {}
    ret["ip_addr"] = ip_addr

    if g is not None:
        ret["country"] = g["country"]["names"]["en"]
        ret["continent"] =  g["continent"]["names"]["en"]
        ret["city"] =  g["city"]["names"]["en"]
        ret["zip"]  =  g["postal"]["code"]
        ret["timezone"] = g["location"]["time_zone"]
        ret["latitude"] =g["location"]["latitude"]
        ret["longitude"] = g["location"]["longitude"]

    else:
        log.warning("cant get geolocation for IP {}".format(ip_addr))
        ret["country"] = UNDEFINED
        ret["continent"] = UNDEFINED
        ret["city"] = UNDEFINED
        ret["timezone"] = UNDEFINED
        ret["latitude"] = 0.0
        ret["longitude"] = 0.0
    return ret