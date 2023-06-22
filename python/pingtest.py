from lib.network import os_ping

# pingHosts = ["192.168.1.1", "google.com", "bbc.co.uk"]
pingHosts = [["192.168.1.1","local"], ["10.10.10.10","local"], ["jhbasdfkjnasfkj.com","inet"]]
pingCount = 1
pingResult = []

for host in pingHosts:
    pingResult.append([host[0], os_ping(host[0], pingCount, host[1])])

print(pingResult)