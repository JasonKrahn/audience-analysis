from aa_backend.caching import RedisCache

if __name__ == '__main__':

    r = RedisCache()

    r._sessdb.flushall()
    r.cache_session("sess1")
    r.cache_session("sess2")
    r.cache_session("sess3")
    r.cache_session("sess4")
    r.cache_session("sess5")
    r.cache_session("sess6")
    r.cache_session("sess7")
    r.cache_session("sess8")
    r.cache_session("sess9")
    r.cache_session("sess10")
    print(r.get_sessions())


