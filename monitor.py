import sys
from network import traceroute

# Targets
targetHost = sys.argv[1]

# Run the traceroute
hostList = traceroute(targetHost)

print(hostList)
