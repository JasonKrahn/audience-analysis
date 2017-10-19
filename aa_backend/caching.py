import redis
from aa_backend.util import get_setting
from aa_backend.img import paint_boxes, resize_img
THUMBNAIL_DB = 0
SESSIONS_DB = 1


class RedisCache(object):
    def __init__(self, *args):
        super(RedisCache, self).__init__(*args)
        self._thumbdb = redis.StrictRedis(host = get_setting("redis", "host"), db = THUMBNAIL_DB,
                                        password=get_setting("redis","key"), ssl=False)
        self._sessdb = redis.StrictRedis(host = get_setting("redis", "host"), db = SESSIONS_DB,
                                        password=get_setting("redis","key"), ssl=False, charset="utf-8", 
                                        decode_responses=True )

        self._expire = get_setting("redis","expire_sec")

    def cache_thumbnail(self, sess_id, img, faces):
        r = self._thumbdb
        size = (get_setting("app","resize_x"), get_setting("app","resize_y"))
        im = paint_boxes(img, faces)
        im = resize_img(im, size)
        r.set(sess_id, im, ex = self._expire)

    def cache_session(self, sess_id):
        r = self._sessdb
        r.sadd("sessions", sess_id)
    
    def cache_sess_detail(self,sess_id, detail_dict):
        r = self._sessdb
        r.hmset(sess_id, detail_dict)
    
    def get_sessions(self):
        return self._sessdb.smembers("sessions")

    def get_session_detail(self, sess_id):
        return self._sessdb.hgetall(sess_id)

    def get_session_thumbnail(self, sess_id):
        return self._thumbdb.get(sess_id)

