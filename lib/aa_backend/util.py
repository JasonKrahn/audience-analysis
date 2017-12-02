import json
import logging
import collections
from flask import jsonify
import yaml, os, sys, subprocess

conf = {}

log = logging.getLogger()
try:
    with open('config.yaml', 'r') as f:
        conf = yaml.load(f)
except FileNotFoundError:
    log.warning("Config file not fould, going with env vars")

EMPTY_RESPONSE = {'num_faces':0, 'smile': 0.0, 'age': 0, 'males': 0, 'females': 0, 'anger': 0.0, 'contempt': 0.0, 'disgust': 0.0, 'fear': 0.0, 'happiness': 0.0, 'neutral': 0.0, 'sadness': 0.0, 'surprise': 0.0}

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


def get_agg_face_attrs(js):
    '''
    TODO: figure out how to reduce code here
    '''

    #handling no face situation
    if js == []:
        log.info("No face. returning empty response")
        return EMPTY_RESPONSE

    faces = 0
    sumFaceAttr = collections.Counter()
    sumEmotionAttr = collections.Counter()

    returnDict = {}

    for i in js:
    #transform json
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









