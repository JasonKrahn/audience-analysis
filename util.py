import json
import logging
import collections


log = logging.getLogger()


def get_agg_face_attrs(js):
    '''
    TODO: figure out how to reduce code here
    '''
    faces = 0
    sumFaceAttr = collections.Counter()
    sumEmotionAttr = collections.Counter()

    returnDict = {}

    for i in js:
    # now song is a dictionary
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


if __name__ == "__main__":
    import yaml, sys, pickle
    with open('config.yaml', 'r') as f: conf = yaml.load(f)
    log.setLevel(logging.getLevelName(conf['app']['log_level']))
    log.addHandler(logging.StreamHandler(stream = sys.stdout))

    js = json.load(open("test_json.pkl"))
    transformed_js = get_agg_face_attrs(js)
    log.debug(str(transformed_js))




