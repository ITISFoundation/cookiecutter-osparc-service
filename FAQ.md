# Frequently Asked Questions (FAQ)


## What dev tools do I need?
 Basically you need makefile and [docker installed](https://docs.docker.com/desktop/install/linux-install/). Nonetheless, there are other tools that are optional but we highly recommend. To
 get more info, just type
 ```cmd
 make info
 ```



## I want to changes some settings. Can I re-run my cookiecutter?

Yes. The first run produces a ``.cookiecutterrc`` file with the current selection. Just change
the values of the settings and type ``make replay``.



## Permission error with docker

```cmd
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: ...  dial unix /var/run/docker.sock: connect: permission denied. See 'docker run --help'.
```
Test first
```
docker run hello-world
```
if you get a similar error then probably the problem is that your user is not allowed to run ``docker``. Basically, create a docker group (sometimes it is already created), add your user to the group, log in to the new docker group, check visually user's group
```cmd
 $ sudo groupadd docker
 $ sudo usermod -aG docker $USER
 $ newgrp docker
 $ id $USER
```
SEE details in https://stackoverflow.com/a/48957722.
