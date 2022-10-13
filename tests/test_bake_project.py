# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable

import json

import subprocess
import sys
from pathlib import Path

from pytest_cookies.plugin import Cookies, Result
import pytest

current_dir = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent
repo_basedir =current_dir.parent
cookiecutter_json = repo_basedir / "cookiecutter.json"



def test_minimal_config_to_bake(cookies: Cookies):
    result = cookies.bake(extra_context={"project_slug": "test_project"})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == "test_project"

    print(f"{result}", f"{result.context=}")


@pytest.fixture(
    params=json.loads(cookiecutter_json.read_text())["docker_base"]
)
def baked_project(cookies: Cookies, request) -> Result:
    result = cookies.bake(
        extra_context={
            "project_slug": "DummyProject",
            "project_name": "dummy-project",
            "default_docker_registry": "test.test.com",
            "docker_base": request.param,
        }
    )

    assert result.exception is None
    assert result.exit_code == 0
    return result


@pytest.mark.parametrize(
    "commands_on_baked_project",
    (
        "ls -la .; make help",
        # TODO: cannot use `source` to activate venvs ... not sure how to proceed here. Suggestions?
        ## "make devenv; source .venv/bin/activate && make build info-build test",
    ),
)
def test_make_workflows(baked_project: Result, commands_on_baked_project: str):
    working_dir = baked_project.project_path
    subprocess.run(
        ["/bin/bash", "-c", commands_on_baked_project], cwd=working_dir, check=True
    )
