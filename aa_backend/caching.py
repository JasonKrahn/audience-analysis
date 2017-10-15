import redis
from util import get_setting
from img import paint_boxes, resize_img

class RedisCache(object):
    def __init__(self, *args):
        super(ClassName, self).__init__(*args))
        self._rconn = redis.StrictRedis(host = get_setting("redis", "host"), 
                                        password=get_setting("redis","key"))
        self._expire = get_setting("redis","expire_sec")

    def cache_thumbnail(sess_id, img, faces):
        r = self._rconn
        size = (get_setting("app","resize_x"), get_setting("app","resize_y"))
        im = paint_boxes(im, faces)
        im = resize_img(im, size)
        r.set(sess_id, im, ex = self._expire)