import subprocess

def traceroute(hostname):
  # Use local OS traceroute command to return a list of IP addresses.
  tracedHosts = []
  traceroute = subprocess.Popen(["traceroute",hostname],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in iter(traceroute.stdout.readline,b""):
      line = line.decode("UTF-8")
      host = line.split("  ")
      if len(host)>1:
          host = host[1].split("(")
          if len(host)>1:
              host = host[1].split(")")
              tracedHosts.append(host[0])
  return tracedHosts
