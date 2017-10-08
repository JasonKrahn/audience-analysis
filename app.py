#!/usr/bin/env python3

import os
import sys
import json
from flask import Flask, request, Response, jsonify
import requests
import logging
import yaml
import util as u

import pickle
from collections import deque



log = logging.getLogger()

app = Flask(__name__, static_url_path="/static")

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
sbs = u.get_ehub()
# two in-memory structures to maintain last faceAttr and last JPEG
sessionLastFaceAttr = deque(maxlen = int(u.get_setting("app","max_sessions")))
sessionLastJPEG = {}

@app.route("/",methods=["GET", "POST"])
def process_image():

    url = "https://" + u.get_setting("cognitive_services", "faceapi_uri") + "/face/v1.0/detect"
    #url = "https://hookb.in/vaP0en5Y"
    #url = "https://requestb.in/10yi8601"
    subscription_key = u.get_setting("cognitive_services","subscription_key")
    sess_id = request.headers["SESSIONID"]

    if request.headers["Content-Type"] == "application/octet-stream":
        headers = {"Content-Type": "application/octet-stream",
                    "Ocp-Apim-Subscription-Key": subscription_key}

        # Request parameters.
        params = {
            "returnFaceId": "true",
            "returnFaceLandmarks": "false",
            "returnFaceAttributes": "age,gender,smile,emotion",
        }

        r = requests.post(url, params = params, headers = headers, data = request.data)

        ret = u.get_agg_face_attrs(r.json())
        ret["session_id"] = sess_id

        sbs.send_event(u.get_setting("event_hubs","hub_name"), json.dumps(ret))

        #save file for testing purposes
        #with open("test_json.pkl", "w") as f:
        #    json.dump(r.json(), f)

        #Updating the session metadata and last JPEG
        resp = {}
        resp["SESSIONID"] = sess_id
        resp["faceAttributes"] = r.json()
        sessionLastFaceAttr.appendleft(resp)
        sessionLastJPEG[sess_id] = request.data

        log.debug(json.dumps(ret))

        return Response(json.dumps({"message":"Success"}), status=200, mimetype="application/json")

    else:
        return u.bad_message("Wrong content type, only octet-stream is supported")

@app.route("/sessions",methods=["GET"])
def get_sessions():
    resp = jsonify({"sessions":list(sessionLastFaceAttr)})
    resp.status_code = 200
    return resp

@app.route("/session-jpeg/<session_id>",methods=["GET"])
def get_session_jpeg(session_id):
    if session_id in sessionLastJPEG:
        return Response(sessionLastJPEG[session_id], status=200, mimetype="application/octet-stream")
    else:
        return u.bad_message("no such session")


if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler(stream = sys.stdout))

    HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    try:
        PORT = int(os.environ.get("SERVER_PORT", "5555"))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)


