import subprocess, logging, config as config
import speedtest, logging
from ping3 import ping
import redis
from config import get_configValue

logger = logging.getLogger(config.loggerName)
redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def traceroute(hostname):
    # Use local OS traceroute command to return a list of IP addresses.
    tracedHosts = []
    traceHops = "6"

    if config.osType == "Linux" or config.osType == "Darwin":
        traceroute = subprocess.Popen(["traceroute","-m",traceHops,hostname],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(traceroute.stdout.readline,b""):
            line = line.decode("UTF-8")
            host = line.split("  ")
            if len(host)>1:
                host = host[1].split("(")
                if len(host)>1:
                    host = host[1].split(")")
                    tracedHosts.append(host[0])
                    logger.debug("Traceroute found host:" + host[0])
    else:
        traceroute = subprocess.Popen(["tracert","-h",traceHops,hostname],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(traceroute.stdout.readline,b""):
            # FIXME doesn't handle when a hop has no DNS lookup and just returns an IP.
            line = line.decode("UTF-8")
            host = line.split("  ")
            if len(host)>1:
                host = host[8].split("[")
                if len(host)>1:
                    host = host[1].split("]")
                    tracedHosts.append(host[0])
                    logger.debug("Traceroute found host:" + host[0])
    
    return tracedHosts

def ping3host(hostname):
    try:
        result = ping(hostname)
    except:
        result = False

    if result == False:
        return 68
    elif result == None:
        return 2
    else:
        return result

def pinghost(hostname):
    if config.osType == "Linux" or config.osType == "Darwin":
        pingResult = subprocess.Popen(["ping",hostname, "-c", "4"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        pingResult = subprocess.Popen(["ping", "-n", "4", hostname],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pingResult.wait()

    """
    Return values
        0 = Success
        2 = No reply
        68 = DNS lookup failed
    """
    return pingResult.poll()


def runSpeedtest():
    # https://github.com/sivel/speedtest-cli/wiki

    redis_conn.set('isspeedtestrunning', 'yes')

    logger.debug("Starting speedtest")
    speedtestserverid = get_configValue('speedtestserverid')

    st = speedtest.Speedtest()
    speedtestServer = ""

    if speedtestserverid == 'Any':
        speedtestServer = st.get_best_server()
    else:
        servers = [speedtestserverid]
        speedtestServer = st.get_servers(servers)

    ping = st.results.ping
    download = st.download()
    upload = st.upload()
    server = st.results.server["sponsor"] + " - " + st.results.server["name"]

    logger.debug("Speedtest using: " + server)

    result = "Ping:" + str(ping) + " Down: " + str(download) + " Up: " + str(upload) + " Server: " + str(server)
    logger.debug("Speedtest results: " + result)

    redis_conn.set('isspeedtestrunning', 'no')

    return st