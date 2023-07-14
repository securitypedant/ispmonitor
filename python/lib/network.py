import subprocess, logging, json, config as config
import logging, psutil, re
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

def checkDefaultGateway(num_pings=1):
    gateways = netifaces.gateways()
    if gateways['default'] == {}:
        pingSuccess = False
        returnMessage = "No default gateway set."
    else:
        default_gateway = gateways['default'][netifaces.AF_INET][0]

        pingReturn = os_ping(default_gateway, num_pings, 'local')

        if pingReturn['response'] == 'failed':
            pingSuccess = False
            returnMessage = default_gateway + " didn't reply: " + pingReturn['response_reason']   
        else:
            pingSuccess = True
            returnMessage = default_gateway + " response: " + pingReturn['timing'][0] + " ms"

    return ["Gateway Status", getDateNow(), pingSuccess, returnMessage]

def checkLocalInterface(which_interface):
    # Is this interface up?
    interfaces = psutil.net_if_stats()
    if which_interface in interfaces:
        interface = interfaces[which_interface]
        return ["Interface Status", getDateNow(), interface.isup, "Network interface '" + which_interface + "' is up? " + str(interface.isup)]
    else:
        return ["Interface Status", getDateNow(), False, "Network interface missing from system: " + which_interface]

def getLocalInterfaces():
    # Return a list of local interface details in a list.
    # return psutil.net_if_stats()
    return psutil.net_if_addrs()

def checkConnection(hosts, pollamount=2):
    """ Ping a list of hosts to determine if current connection is working correctly. """
    returnDict = []
    failedHosts = 0
    pingReturnDict = []

    for host in hosts:
    # Ping target to determine if network is available.
        hostname = host[0]
        hosttype = host[1]
        logger.debug("Pinging " + hostname)
        
        # Ping the host once,
        pingReturn = os_ping(hostname, pollamount, hosttype)

        # ['success',[[google.com, 35, 'Success'][bbc.co.uk, 20, 'Success']]]
        # ['partial',[[google.com, 35, 'Success'][bbc.co.uk, 0, 'CannotResolve']]]
        # ['failed',[[google.com, 0, 'Timeout'][bbc.co.uk, 0, 'Timeout']]]

        if pingReturn['response'] == 'success':
            # Host is reachable
            logger.debug("Success reaching " + hostname)
            pingReturnDict.append([hostname, float(pingReturn['timing'][0]), 'success'])
        elif pingReturn['response'] == 'failed':
            # False when Ping cannot resolve hostname
            logger.warning(pingReturn['response_reason'] + ":" + hostname + " code:" + str(pingReturn['code']))
            pingReturnDict.append([hostname, 0, pingReturn['response_reason']])
            failedHosts = failedHosts + 1

    if failedHosts == 0:
        returnDict = ['success',pingReturnDict]
    elif failedHosts == len(hosts):
        # All hosts failed to return a response.
        returnDict = ['failed',pingReturnDict]
    else:
        # At least one host failed to respond.
        returnDict = ['partial',pingReturnDict]
        
    return returnDict

def checkNetworkHops(hops):
    """ Check a list of IP4 addresses to see if we can contact them. Check in order of a traceroute result. """
    hop_check_result = []
    traceroute_success = True
    for hop in hops:
        if checkNetworkIP4Address(hop):
            hop_check_result.append("success:" + str(hop))
        else:
            hop_check_result.append("failed:" + str(hop))
            traceroute_success = False

    return ["Traceroute results", getDateNow(), traceroute_success, hop_check_result]

def checkNetworkIP4Address(hop):
    """ Try to contact an IP4 network address and determine if we can communicate with it. """
    ping_return = os_ping(hop)

    if ping_return == 'failed':
        # Ping failed
        return False
    else:
        # Ping success
        return True

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

def os_ping(host, count=4, type='inet'):
    """ Ping an IP4 network address returning a dict with information.
        type parameters refines the ping command, like so.
        inet = An internet address which may take several seconds to reply.
        local = A LAN or very close WAN address we expect to be millisecond in response.
    """
    returnDict = {}
    returnDict['host'] = host
    returnDict['hosttype'] = type
    returnDict['pingcount'] = count

    if config.osType == "Darwin":
        if type == 'local':
            response_timeout = '250'
        elif type == 'inet':
            response_timeout = '1000'
        ping_command = ['ping', '-W', response_timeout, '-c', str(count), host]

    elif config.osType == "Linux":
        response_timeout = '1'
        ping_command = ['ping', '-W', response_timeout, '-c', str(count), host]

    else:
        ping_command = ['ping', '-n', str(count), host]
    
    ping_output = subprocess.run(ping_command, capture_output=True, text=True)

    if ping_output.returncode == 0:
        returnDict['response'] = "success"
        returnDict['response_reason'] = "success"
        # extract the response time from the output, depends on platform.
        if config.osType == "Darwin" or config.osType == "Linux":
            pattern = r"time=([\d.]+) ms"
        else:
            pattern = r"Average = ([\d.]+)ms"
        response_times = re.findall(pattern, ping_output.stdout)
        returnDict['timing'] = response_times
        response_times_floats = [float(num) for num in response_times]
        returnDict['avg_timing'] = str(sum(response_times_floats) / len(response_times_floats))
    elif ping_output.returncode == 2:
        returnDict['response'] = "failed"
        returnDict['response_reason'] = "no response"
    elif ping_output.returncode == 68:
        returnDict['response'] = "failed"
        returnDict['response_reason'] = "unknown host"
    else:
        returnDict['response'] = "failed"
        returnDict['response_reason'] = "unknown"
        
    returnDict['code'] = ping_output.returncode
    return returnDict

def run_osSpeedtest():
    """ Run a speedtest using the Ookla CLI tool, which allows returning results as json """
    redis_conn.set('isspeedtestrunning', 'yes')
    logger.debug("Starting speedtest")
    speedtestserverid = get_configValue('speedtestserverid')
    
    if speedtestserverid != 'Any':
        serverIDcmd = speedtestserverid
    else:
        serverIDcmd = ""
    
    try:
        output_bytes = subprocess.check_output(['speedtest', "-s", serverIDcmd, "--format=json", "--accept-license"])
    except Exception as inst:
        logger.error("Speedtest failed in function: " + inst)
    
    output = json.loads(output_bytes.decode('utf-8'))

    result = "Ping:" + str(output['ping']['latency']) + " Down: " + str(output['download']['bytes'] / 1000 / 1000) + " Up: " + str(output['upload']['bytes'] / 1000 / 1000) + " Server: " + output['server']['host']
    
    redis_conn.set('lastspeedtest', json.dumps({"ping": str(output['ping']['latency']), 
                                                "download": str(round(output['download']['bytes'] / 1000 / 1000, 2)), 
                                                "upload": str(round(output['upload']['bytes'] / 1000 / 1000, 2)), 
                                                "server": str(output['server']['host'])})
                                                )
    logger.debug("Speedtest results: " + result)
    redis_conn.set('isspeedtestrunning', 'no')

    return output

def runSpeedtest():
    # https://github.com/sivel/speedtest-cli/wiki
    # 18531 - Wave in San Francisco, CA

    redis_conn.set('isspeedtestrunning', 'yes')

    logger.debug("Starting speedtest")
    speedtestserverid = get_configValue('speedtestserverid')

    st = speedtest.Speedtest(secure=1)

    if speedtestserverid != 'Any':
        servers = [speedtestserverid]
        # TODO: Fix the speedtest.NoMatchedServers error. 
        st.get_servers(servers)

    st.get_best_server()

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