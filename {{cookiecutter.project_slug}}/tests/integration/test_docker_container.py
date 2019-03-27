# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import filecmp
import os
import shutil
from pathlib import Path
from pprint import pformat
from typing import Dict

import docker
import pytest

_FOLDER_NAMES = ["input", "output", "log"]
_CONTAINER_FOLDER = Path("/home/scu/data")

@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()

@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient) -> str:
    image_key = "simcore/services/{%- if cookiecutter.project_type == 'computational' -%}comp{%- elif cookiecutter.project_type == 'dynamic' -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest"
    docker_images = [image for image in docker_client.images.list() if any(image_key in tag for tag in image.tags)]
    return docker_images[0].tags[0]

def _is_gitlab_executor() -> bool:
    return "GITLAB_CI" in os.environ

@pytest.fixture
def temporary_path(tmp_path: Path) -> Path:
    if _is_gitlab_executor():
        # /builds is a path that is shared between the docker in docker container and the job builder container
        shared_path = Path("/builds/{}/tmp".format(os.environ["CI_PROJECT_PATH"]))
        shared_path.mkdir(parents=True, exist_ok=True)
        return shared_path
    return tmp_path

@pytest.fixture
def host_folders(temporary_path: Path) -> Dict:
    tmp_dir = temporary_path

    host_folders = {}
    for folder in _FOLDER_NAMES:
        path = tmp_dir / folder
        if path.exists():
            shutil.rmtree(path)
        path.mkdir()
        # we need to ensure the path is writable for the docker container (Gitlab-CI case)
        os.chmod(str(path), 0o775)
        assert path.exists()
        host_folders[folder] = path

    return host_folders

@pytest.fixture
def container_variables() -> Dict:
    # of type INPUT_FOLDER=/home/scu/data/input
    env = {"{}_FOLDER".format(str(folder).upper()):(_CONTAINER_FOLDER / folder).as_posix() for folder in _FOLDER_NAMES}
    return env

@pytest.fixture
def validation_folders(validation_dir: Path) -> Dict:
    return {folder:(validation_dir / folder) for folder in _FOLDER_NAMES}

def test_run_container(validation_folders: Dict, host_folders: Dict, docker_client: docker.DockerClient, docker_image_key: str, container_variables: Dict):
    # copy files to input folder, copytree needs to not have the input folder around.
    host_folders["input"].rmdir()
    shutil.copytree(validation_folders["input"], host_folders["input"])
    assert Path(host_folders["input"]).exists()
    # run the container (this may take some time)
    try:
        volumes = {host_folders[folder]:{"bind":container_variables["{}_FOLDER".format(str(folder).upper())]} for folder in _FOLDER_NAMES}
        container = docker_client.containers.run(docker_image_key,
            "run", detach=True, remove=False, volumes=volumes, environment=container_variables)
        response = container.wait()
        if response["StatusCode"] > 0:
            logs = container.logs(timestamps=True)
            pytest.fail("The container stopped with exit code {}\n\n\ncommand:\n {}, \n\n\nlog:\n{}".format(response["StatusCode"],
            "run", pformat(
                (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
                )))
    except docker.errors.ContainerError as exc:
        # the container did not run correctly
        pytest.fail("The container stopped with exit code {}\n\n\ncommand:\n {}, \n\n\nlog:\n{}".format(exc.exit_status,
            exc.command, pformat(
                (container.logs(timestamps=True).decode("UTF-8")).split("\n"), width=200
                )))
    finally:
        #cleanup
        container.remove()

    for folder in _FOLDER_NAMES:
        # test if the files that should be there are actually there and correct
        list_of_files = [x.name for x in validation_folders[folder].iterdir() if not ".gitkeep" in x.name]
        for file_name in list_of_files:
            assert Path(host_folders[folder] / file_name).exists(), "missing files in {}".format(host_folders[folder])
        match, mismatch, errors = filecmp.cmpfiles(host_folders[folder], validation_folders[folder], list_of_files, shallow=False)
        # assert not mismatch, "wrong/incorrect files in {}".format(host_folders[folder])
        assert not errors, "missing files in {}".format(host_folders[folder])
        # test if the files that are there are matching the ones that should be
        if folder != "input":
            list_of_files = [x.name for x in host_folders[folder].iterdir()  if not ".gitkeep" in x.name]
            for file_name in list_of_files:
                assert Path(validation_folders[folder] / file_name).exists(), "{} is not present in {}".format(file_name, validation_folders[folder])
            match, mismatch, errors = filecmp.cmpfiles(host_folders[folder], validation_folders[folder], list_of_files, shallow=False)
            # assert not mismatch, "wrong/incorrect generated files in {}".format(host_folders[folder])
            assert not errors, "too many files in {}".format(host_folders[folder])
