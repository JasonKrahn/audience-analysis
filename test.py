import redis

from aa_backend.util import get_setting

if __name__ == '__main__':
    conn = redis.StrictRedis(host = get_setting("redis", "host"), db = 1,
                                        password=get_setting("redis","key"), ssl=False )

    d = {"a":" som vale", "b":"ntother"}

    #conn.hmset("testdict", d)
    #d2 = conn.hgetall("testdict")

    #print (d2)   
    print(conn.info("keyspace"))