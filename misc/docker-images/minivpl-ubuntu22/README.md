# VPLBdx Project related docker base image

![VPL Logo](https://github.com/GuillaumeBlin/vplbdx/raw/master/misc/img/VPLBDXLOGO.png)

The VPLBDX project is an alternative execution sandbox to the [VPL-Jail-System](https://github.com/jcrodriguez-dis/vpl-xmlrpc-jail) provided for the [VPL Moodle plugin](https://github.com/jcrodriguez-dis/moodle-mod_vpl). This solution is based on docker swarm, docker containers and a python proxy allowing interactive execution both textual and graphical, and non-iterative execution for code evaluation purpose.

For more details about VPL, visit the [VPL home page](http://vpl.dis.ulpgc.es). The main benefit of this project is to be able to define a personalised sandbox environment for each VPL activity based on a minimal docker image called [gblin/minivpl](https://hub.docker.com/r/gblin/minivpl).

This image is the base docker image from which each docker image used in the VPLBdx project should be built upon.
