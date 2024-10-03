from tempfile import mkstemp
from os import fdopen, remove
from shutil import move, copymode
from typing import Any

import yaml


def get_setup(yaml_file: str) -> dict[str, Any]:
    """Initialize the setup dictionary from the YAML config file.

    Parameters
    ----------
    path: str
        The path to the YAML file.

    Returns
    -------
    dict[str, Any]
        The dictionary with the experiment configuration.
    """

    with open(yaml_file, "r") as f:
        doc = yaml.safe_load(f)
    return doc


def replace(file_path, pattern, subst) -> None:
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)
