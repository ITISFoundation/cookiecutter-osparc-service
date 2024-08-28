# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable

import json

import subprocess
import sys
import os
from pathlib import Path
import datetime, time

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
            "author_email": "you@example.com",
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
        # "ls -la .; make help",
        # TODO: cannot use `source` to activate venvs ... not sure how to proceed here. Suggestions?
        # No need whatsoever, venv only needed for cookiecutter - once it is build, can use "make build" directly
        "make build",
    ),
)
def test_make_workflows(baked_project: Result, commands_on_baked_project: str):
    working_dir = baked_project.project_path
    results = subprocess.run(
        ["/bin/bash", "-c", commands_on_baked_project], cwd=working_dir, 
        # check=True, 
        capture_output=True,
    )
            
    if results.returncode != 0:
        current_time = datetime.datetime.now().strftime("%Y%m%d.%H%M%S%d"); time.sleep(1) # make sure not two test w same name
        output_std_dir = current_dir.parent / "tmp" / "stderr"
        os.makedirs(output_std_dir, exist_ok=True)
        with open(output_std_dir / f"stderr_{current_time}.txt", "w+") as f:
            print(results.stderr.decode(), file=f)
        raise RuntimeError("Subprocess did not run correctly")
