#!/bin/bash
xhost +local:docker

if grep -q "^\s*X11Forwarding\s+yes" "/etc/ssh/sshd_config"; then
  echo WARNING : better having better having "X11Forwarding yes" in /etc/ssh/sshd_config
fi
if grep -q "^\s*X11UseLocalhost\s+no" "/etc/ssh/sshd_config"; then
  echo WARNING : better having better having "X11UseLocalhost no" in /etc/ssh/sshd_config
fi


