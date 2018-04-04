#!/usr/bin/env python3

import os
import sys
import json
from flask import Flask, request, Response, jsonify, render_template, url_for
#from flask_cors import CORS
import requests
import logging


sys.path.append("./lib")
sys.path.append("./submodules/pypbi")

import aa_backend.util as u
import aa_backend.messaging as msg
import aa_backend.caching as cache
from aa_backend.geo import get_geo

import aa_backend.pbi as pbi

import pickle
from collections import deque



log = logging.getLogger()

app = Flask(__name__, static_url_path="/static")
#CORS(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# messaging and caching
sbs = msg.get_ehub()
redis_cache = cache.RedisCache()


# two in-memory structures to maintain last faceAttr and last JPEG
#sessionLastFaceAttr = deque(maxlen = int(u.get_setting("app","max_sessions")))
#sessionLastJPEG = {}

@app.route('/')
def hello():
    return redirect(url_for('dashboard'))

@app.route("/camera", methods=["GET"])
def serve_camera():
    return render_template("camera_index.htm")

@app.route("/dashboard",methods=["GET"] )
def serve_dashboard():
    #send_from_directory(filename="dashboard/index.html")
    return render_template("dash_index.htm")

@app.route('/api/report-token')
def get_token():
    j = pbi.get_report_token()
    return j, 200, {'Content-Type': 'application/json'}

@app.route('/api/dashboard-token')
def get_token():
    j = pbi.get_dashboard_token()
    return j, 200, {'Content-Type': 'application/json'}



@app.route("/api/faces",methods=["GET", "POST"])
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
        #log.debug(str(r.json()) )

        try:
            ret = u.get_agg_face_attrs(r.json())
        except AttributeError:
            log.error("Face Api returned unexpected response")
            return u.bad_message("Face API returned unexpected response")
        ret["session_id"] = sess_id
        log.debug("Sending response to the event hub: " + str(ret))

        #getting geodata
        ip_addr = request.access_route[0]

        if ":" in ip_addr:
            ip_addr = ip_addr.split(":")[0]

        log.debug("request.access_route: {}".format(request.access_route))
        log.debug("x-forwarded-for: {}".format(request.headers.getlist("X-Forwarded-For")))

        #if request.headers.getlist("X-Forwarded-For"):
        #    ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        #else:
        #    ip_addr = request.remote_addr

        ret.update(get_geo(ip_addr))


        sbs.send_event(u.get_setting("event_hubs","hub_name"), json.dumps(ret))

        if "FULL_IMG" in request.headers:
            redis_cache.cache_img(sess_id, request.data)
        else:
            # caching thumbnail to redis
            redis_cache.cache_thumbnail(sess_id = sess_id, img = request.data, faces = r.json())
            redis_cache.cache_session(sess_id)


        #save file for testing purposes
        #with open("test_json.json", "w") as f:
        #    json.dump(r.json(), f)

        #Updating the session metadata and last JPEG
        resp = {}
        resp["SESSIONID"] = sess_id
        resp["faceAttributes"] = r.json()

        redis_cache.cache_sess_detail(sess_id, resp)


        return Response(json.dumps({"message":"Success"}), status=200, mimetype="application/json")

    else:
        return u.bad_message("Wrong content type, only octet-stream is supported")

@app.route("/api/sessions",methods=["GET"])
def get_sessions():
    sessions = list(redis_cache.get_sessions())
    cnt = redis_cache.get_session_count()
    log.debug("List of sessions : {}".format(sessions))
    resp = jsonify({"sessions":sessions, "session_count": cnt})
    resp.status_code = 200
    return resp

@app.route("/api/session-jpeg/<session_id>",methods=["GET"])
def get_session_jpeg(session_id):
    thumb = redis_cache.get_session_thumbnail(session_id)
    if thumb is not None:
        return Response(thumb, status=200, mimetype="application/octet-stream")
    else:
        return u.bad_message("no such session")

''' @app.route("/session-detail/<session_id>",methods=["GET"])
def get_session_jpeg(session_id):
    det = redis_cache.get_session_detail(session_id)
    if det is not None:
        return Response(det, status=200, mimetype="application/json")
    else:
        return u.bad_message("no such session")
 '''

# No cacheing at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == "__main__":
    log.setLevel(u.get_setting("app", "log_level"))
    formatter = logging.Formatter('[%(asctime)s] {%(module)s.%(funcName)s:%(lineno)d %(levelname)s} - %(message)s')
    #'%m-%d %H:%M:%S'
    handl = logging.StreamHandler(stream = sys.stdout)
    handl.setFormatter(formatter)
    log.addHandler(handl)

    #cleaning all datasets after the app restart
    pbi.flush_powerbi()

    #flushing redis
    redis_cache.flushall()

    HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    try:
        PORT = int(os.environ.get("SERVER_PORT", "5555"))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)


