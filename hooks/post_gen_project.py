#
# When the hook scripts script are run, their current working directory is the root of the generated project
#
# SEE https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html

# pylint: disable=missing-function-docstring
# pylint: disable=unspecified-encoding

import os
import re
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

import yaml

SELECTED_DOCKER_BASE = "{{ cookiecutter.docker_base }}"
SELECTED_GIT_REPO = "{{ cookiecutter.git_repo }}"
METADATA_PATH = (
    "{{ cookiecutter._output_dir }}/{{cookiecutter.project_slug}}/.osparc/metadata.yml"
)


@contextmanager
def _context_print(msg: str):
    print(msg, end="...", flush=True)
    yield
    print("DONE")


def _create_dockerfile():
    folder_name = Path("docker") / SELECTED_DOCKER_BASE.split(":", maxsplit=1)[0]

    # list folders
    # NOTE: it needs to be a list as we delete the folders

    for folder in list(f for f in Path("docker").glob("*") if f.is_dir()):
        if folder != folder_name:
            shutil.rmtree(folder)


def _create_ignore_listings():
    # .gitignore
    common_gitignore = Path("Common.gitignore")
    python_gitignore = Path("Python.gitignore")

    gitignore_file = Path(".gitignore")
    gitignore_file.unlink(missing_ok=True)
    shutil.copyfile(common_gitignore, gitignore_file)

    if "python" in SELECTED_DOCKER_BASE:
        with gitignore_file.open("at") as fh:
            fh.write("\n")
            fh.write(python_gitignore.read_text())

    common_gitignore.unlink()
    python_gitignore.unlink()

    # .dockerignore
    common_dockerignore = Path("Common.dockerignore")
    dockerignore_file = Path(".dockerignore")
    dockerignore_file.unlink(missing_ok=True)
    shutil.copyfile(common_dockerignore, dockerignore_file)

    # appends .gitignore above
    with dockerignore_file.open("at") as fh:
        fh.write("\n")
        fh.write(gitignore_file.read_text())

    common_dockerignore.unlink()


def _create_repo_folder():
    if SELECTED_GIT_REPO != "github":
        shutil.rmtree(".github")
    if SELECTED_GIT_REPO != "gitlab":
        shutil.rmtree(".gitlab")


def _postpro_osparc_metadata():
    metadata_path = Path(METADATA_PATH)
    content = metadata_path.read_text()
    metadata = yaml.safe_load(content)
    if metadata.get("version") == metadata.get("version_display", "UNDEFINED"):
        with _context_print(
            "metadata: version_display==version, removing version_display"
        ):
            # NOTE: prefer to substitue than re-serialize with yaml to avoid risk of
            # reformatting values
            pattern = re.compile(r"^version_display:.*\n?", re.MULTILINE)
            metadata_path.write_text(pattern.sub("", content))


def main():
    print("Starting post-gen-project hook:", flush=True)
    try:
        with _context_print("Pruning docker/ folder to selection"):
            _create_dockerfile()

        with _context_print("Updating .gitignore and .dockerignore configs"):
            _create_ignore_listings()

        with _context_print("Adding config for selected external repository"):
            _create_repo_folder()

        
        _postpro_osparc_metadata()

    except Exception as exc:  # pylint: disable=broad-except
        print("ERROR", exc)
        return os.EX_SOFTWARE
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
