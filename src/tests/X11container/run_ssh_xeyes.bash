#/usr/bin/bash
echo CTRL-C to quit
docker run --rm -it --net=host --env DISPLAY=:0.0 ssh_xeyes
