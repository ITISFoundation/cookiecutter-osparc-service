# cookiecutter-osparc-service

Status: ![Build Status](https://github.com/ITISFoundation/cookiecutter-osparc-service/workflows/Github-CI%20Push/PR/badge.svg)

Cookiecutter to generate an oSparc compatible service for the oSparc simcore platform. Currently only for **computational services** supported.


## Requirements
- GNU Make
- Python3
- Python3-venv (recommended to work in a virtual environment)
- [``cookiecutter``](https://python-package-generator.readthedocs.io/en/master/)

```console
sudo apt-get update
sudo apt-get install -y make python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install cookiecutter
```

## Usage

Generate a new Cookiecutter template layout:
```console
python3 -m venv .venv
source .venv/bin/activate
cookiecutter gh:ITISFoundation/cookiecutter-osparc-service
```

Check [FAQ](./FAQ.md)

## Tutorials and guides
A video tutorial is available:

[![webinar_preview](https://img.youtube.com/vi/yoKXHMQcs1Y/0.jpg)](https://www.youtube.com/watch?v=yoKXHMQcs1Y)

## Development

```console
git clone https://github.com/ITISFoundation/cookiecutter-osparc-service.git
cd cookiecutter-osparc-service
make devenv
source .venv/bin/activate
make play
make tests
```

## License

This project is licensed under the terms of the [MIT License](/LICENSE)


---

<p align="center">
<img src="https://forthebadge.com/images/badges/built-with-love.svg" width="150">
</p>
