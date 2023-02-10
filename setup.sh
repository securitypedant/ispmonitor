#!/bin/bash

################################################################################
##       ISP Monitor - Comprehensive ISP connection monitoring                ##
##       https://github.com/securitypedant/ispmonitor                         ##
##                                       -- Simon Thorpe                      ##
################################################################################

VAR_SCRIPTLOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VAR_PYTHONBINLOC="$(which python)"

HELP_DISPLAY() {
  echo "This script sets up the ISPMonitor Python tool:"
  echo
  echo "$VAR_SCRIPTNAME -h                                       Display help information"
  echo "$VAR_SCRIPTNAME -i                                   Install as a systemd service"
  echo
}

CONFIGURE_PYTHON_APP() {

}

INSTALL_SYSTEMD_SERVICE() {
  if ! command -v systemctl &> /dev/null; then
    echo "Cannot find Systemctl."
    echo "ISPMonitor requires systemctl to install as a service."
    echo "Please installed systemd package."
    exit
  else 
    FILE=/etc/systemd/system/ispmonitor.service
    if [ -f "$FILE" ]; then
      echo "ISPMonitor service already exists."
      echo "Use systemctl status ispmonitor to view details."
      exit
    else
      echo "Installing ISPMonitor service..."
      sudo tee -a /etc/systemd/system/ispmonitor.service <<EOL >/dev/null
[Unit]
Description=ISP Monitor Service
After=multi-user.target
[Service]
Type=simple
Restart=always
WorkingDirectory=$VAR_SCRIPTLOC/
ExecStart=$VAR_PYTHONBINLOC $VAR_SCRIPTLOC/main.py
[Install]
WantedBy=multi-user.target
EOL
      sudo systemctl enable ispmonitor.service >/dev/null
      echo "Would you like to start ispmonitor as a service now?"
      echo -n "(y/n): "
      read answer
      if [ "$answer" != "${answer#[Yy]}" ] ;then
        sudo systemctl start ispmonitor
        exit
      else
        exit
      fi
    fi
  fi
}

CONFIGURE_PYTHON_APP
INSTALL_SYSTEMD_SERVICE