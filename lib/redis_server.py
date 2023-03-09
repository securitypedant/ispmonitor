import redis, logging, config as config
import sys

logger = logging.getLogger(config.loggerName)

# redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379. No connection could be made because the target machine actively refused it.
def getRedisConn():
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    try:
        redis_conn.ping()
    except redis.exceptions.ConnectionError:
        logger.critical("Unable to connect to redis server.")
        print("Unable to connect to redis server.")
    except Exception as e:
        logger.critical("Unable to connect to redis server.")
        print("Unable to connect to redis server.")
    else:
        return redis_conn