import subprocess, logging, config
import speedtest

def traceroute(hostname):
    # Use local OS traceroute command to return a list of IP addresses.
    tracedHosts = []
    traceHops = "6"

    if config.osType == "Linux":
        traceroute = subprocess.Popen(["traceroute","-m",traceHops,hostname],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(traceroute.stdout.readline,b""):
            line = line.decode("UTF-8")
            host = line.split("  ")
            if len(host)>1:
                host = host[1].split("(")
                if len(host)>1:
                    host = host[1].split(")")
                    tracedHosts.append(host[0])
                    logging.debug("Traceroute found host:" + host[0])
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
                    logging.debug("Traceroute found host:" + host[0])
    
    return tracedHosts

def pinghost(hostname):
    pingResult = subprocess.Popen(["ping",hostname, "-c", "4"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
    logging.debug("Starting speedtest")
    st = speedtest.Speedtest()
    st.get_best_server()

    ping = st.results.ping
    download = st.download()
    upload = st.upload()
    server = st.results.server["sponsor"] + " " + st.results.server["name"]

    result = "Ping:" + str(ping) + " Down: " + str(download) + " Up: " + str(upload) + " Server: " + str(server)
    logging.debug("Speedtest results: " + result)

    return st