from geolite2 import geolite2
UNDEFINED = "Undefined"
import logging
log = logging.getLogger()

def get_geo(ip_addr):
    geo_reader = geolite2.reader()
    g = None

    try:
        g = geo_reader.get(ip_addr)
    except ValueError:
        log.error("parsing IP address: {} failed!".format(ip_addr))

    log.debug("Geo data :" +  str(g))
    ret = {}
    ret["ip_addr"] = ip_addr

    if g is not None:
        ret["country"] = g.get("country",{}).get("names",{}).get("en", UNDEFINED)
        ret["continent"] =  g.get("continent",{}).get("names",{}).get("en", UNDEFINED)
        ret["city"] =  g.get("city",{}).get("names",{}).get("en", UNDEFINED)
        ret["zip"]  =  g.get("postal",{}).get("code",UNDEFINED)
        ret["timezone"] = g.get("location",{}).get("time_zone",UNDEFINED)
        ret["latitude"] =g.get("location",{}).get("latitude")
        ret["longitude"] = g.get("location",{}).get("longitude")

    else:
        log.warning("cant get geolocation for IP {}".format(ip_addr))
        ret["country"] = UNDEFINED
        ret["continent"] = UNDEFINED
        ret["city"] = UNDEFINED
        ret["timezone"] = UNDEFINED
        ret["latitude"] = 0.0
        ret["longitude"] = 0.0
    return ret