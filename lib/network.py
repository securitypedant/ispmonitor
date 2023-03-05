import subprocess, logging, json, config as config
import speedtest, logging, psutil
from ping3 import ping
import redis, netifaces, dns.resolver
from config import get_configValue
from lib.datastore import getDateNow
from lib.redis_server import getRedisConn

logger = logging.getLogger(config.loggerName)

redis_conn = getRedisConn()    

def checkDNSServers(host):
    # https://dnspython.readthedocs.io/en/stable/index.html
    resolver = dns.resolver.Resolver()

    dns_servers = resolver.nameservers
    dns_check_result = []
    dns_checks_success = True

    for server in dns_servers:
        resolver.nameservers = [server]
        try:
            answer = resolver.resolve(host, "A")
        except Exception as e:
            dns_checks_success = False
            dns_check_result.append([server, e.msg]) 
        else:
            if type(answer) == dns.resolver.Answer:
                dns_check_result.append([server, True])

    return ["DNS Server Status for " + host, getDateNow(), dns_checks_success, "DNS server response " + str(dns_check_result)]

def checkDefaultGateway():
    gateways = netifaces.gateways()
    if gateways['default'] == {}:
        pingSuccess = False
        returnMessage = "No default gateway"
    else:
        default_gateway = gateways['default'][netifaces.AF_INET][0]

        pingReturn = ping(default_gateway, unit='ms')

        if isinstance(pingReturn, (int, float, complex)):
            pingSuccess = True
        else:
            pingSuccess = False
            returnMessage = default_gateway + " didn't reply: " + pingReturn
        
        returnMessage = default_gateway + " response: " + str(round(pingReturn))

    return ["Gateway Status", getDateNow(), pingSuccess, returnMessage]

def checkLocalInterface(which_interface):
    # Is this interface up?
    interfaces = psutil.net_if_stats()
    interface = interfaces[which_interface]

    return ["Interface Status", getDateNow(), interface.isup, "Network interface '" + which_interface + "' is up? " + str(interface.isup)]

def getLocalInterfaces():
    # Return a list of local interface details in a list.
    # return psutil.net_if_stats()
    return psutil.net_if_addrs()

def checkConnection(hosts):
    failedHosts = 0
    returnDict = []
    pingReturnDict = []

    for host in hosts:
    # Ping target to determine if network is available.
        logger.debug("Pinging " + host)
        
        # https://pypi.org/project/ping3/
        # Ping the host once, default timeout is 4 seconds.
        pingReturn = ping(host, unit='ms')

        # ['Success',[[google.com, 35, 'Success'][bbc.co.uk, 20, 'Success']]]
        # ['Partial',[[google.com, 35, 'Success'][bbc.co.uk, 0, 'LookupFailed']]]
        # ['Failed',[[google.com, 0, 'Timeout'][bbc.co.uk, 0, 'Timeout']]]

        if pingReturn:
            # Host is reachable
            logger.debug("Success reaching " + host)
            pingReturnDict.append([host,pingReturn,'Success'])
        elif not pingReturn:
            # False when Ping cannot resolve hostname
            logger.warning("Cannot resolve " + host)
            pingReturnDict.append([host,0,'CannotResolve'])
            failedHosts = failedHosts + 1
        else:
            # None when Ping timesout trying to connect.
            logger.warning("Timeout pinging " + host)
            pingReturnDict.append([host,0,'Timeout'])
            failedHosts = failedHosts + 1

    if failedHosts == 0:
        returnDict = ['Success',pingReturnDict]
    elif failedHosts == len(hosts):
        # All hosts failed to return a response.
        returnDict = ['Failed',pingReturnDict]
    else:
        # At least one host failed to respond.
        returnDict = ['Partial',pingReturnDict]
    
    return returnDict

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
    
    return ["Traceroute", getDateNow(), True, tracedHosts]

def ping3host(hostname):
    # https://pypi.org/project/ping3/
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
    # 18531 - Wave in San Francisco, CA

    redis_conn.set('isspeedtestrunning', 'yes')

    logger.debug("Starting speedtest")
    speedtestserverid = get_configValue('speedtestserverid')

    st = speedtest.Speedtest(secure=1)
    speedtestServer = ""

    if speedtestserverid == 'Any':
        speedtestServer = st.get_best_server()
    else:
        servers = [speedtestserverid]
        # TODO: Fix the speedtest.NoMatchedServers error. 
        speedtestServer = st.get_servers(servers)

    ping = st.results.ping
    download = round(st.download() / 1000 / 1000, 2)
    upload = round(st.upload() / 1000 / 1000, 2)
    server = st.results.server["sponsor"] + " - " + st.results.server["name"]

    logger.debug("Speedtest using: " + server)

    result = "Ping:" + str(ping) + " Down: " + str(download) + " Up: " + str(upload) + " Server: " + str(server)
    redis_conn.set('lastspeedtest', json.dumps({"ping":ping, "download": download, "upload": upload, "server":server}))
    logger.debug("Speedtest results: " + result)

    redis_conn.set('isspeedtestrunning', 'no')

    return st