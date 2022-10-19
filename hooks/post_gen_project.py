#
# When the hook scripts script are run, their current working directory is the root of the generated project
#
# SEE https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html

import shutil
import sys
from pathlib import Path
import os


selected_flavor = "{{ cookiecutter.docker_base }}"


def create_dockerfile():
    folder_name = Path("docker") / selected_flavor.split(":")[0]

    # list folders
    # NOTE: it needs to be a list as we delete the folders
    for folder in list(Path("docker").glob("*/**")):
        if folder.exists() and folder != folder_name:
            shutil.rmtree(folder)


def create_ignore_listings():
    # .gitignore
    common_gitignore = Path("Common.gitignore")
    python_gitignore = Path("Python.gitignore")

    gitignore_file = Path(".gitignore")
    gitignore_file.unlink(missing_ok=True)
    shutil.copyfile(common_gitignore, gitignore_file)

    if "python" in selected_flavor:
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


def main():
    try:
        create_dockerfile()
        create_ignore_listings()
    except Exception as exc:  # pylint: disable=broad-except
        print(exc)
        return os.EX_SOFTWARE
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
