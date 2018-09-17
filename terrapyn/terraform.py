import os
import tempfile
import pathlib

import delegator
import semver

from . import environment
from .exceptions import DependencyNotFound


class BaseCommand:
    @classmethod
    def _which(command):
        """Emulates the system's which -a."""

        _which = "where" if os.name == "nt" else "which -a"

        c = delegator.run(f"{_which} {command}")

        try:
            # Which Not found…
            if c.return_code == 127:
                raise DependencyNotFound(
                    "Please install terraform (or provide its path)."
                )
            else:
                assert c.return_code == 0
        except AssertionError:
            return []

        return (c.out.strip() or c.err.strip()).split("\n")


class Terraform(BaseCommand):
    def __init__(self, *, working_dir=None, environ=None):
        self.environ = environment.evaluate(environ=environ)
        self._version = None
        self._temp_dir = None
        if working_dir:
            self._working_dir = pathlib.Path(working_dir)
        else:
            self._working_dir = None

        self.setup()
        self._sanity_check()

    def __repr__(self):
        return f"<TerraformCommand version={self.version!r}>"

    def __enter__(self):
        if not self.temp_dir:
            self.setup()

    def __exit__(self, type, value, tb):
        self.cleanup()

    def setup(self):
        if not self.temp_dir and self.temp_dir is not False:
            self.temp_dir

    def cleanup(self):
        if self.temp_dir:
            os.rmdir(self.temp_dir)
            self._temp_dir = False

    @property
    def version(self):
        return f"{self._version['major']}.{self._version['minor']}.{self._version['patch']}"

    @property
    def temp_dir(self):
        if not self._temp_dir:
            self._temp_dir = pathlib.Path(
                tempfile.mkdtemp(suffix="-terraform-plan", prefix="terrapyn-")
            )

        return self._temp_dir

    @property
    def working_dir(self):
        # Make the working directory, if it doesn't already exist.
        if self._working_dir:
            os.makedirs(self._working_dir, exist_okay=True)
            return self._working_dir
        else:
            return self.temp_dir

    def tf(self, *args, output=True):
        # Change to working directory.
        os.chdir(self.temp_dir)

        cmd = [self.environ["TERRAFORM_PATH"]] + list(args)
        c = delegator.run(
            cmd, timeout=self.environ["TERRAPYN_TIMEOUT"], cwd=self.working_dir
        )
        if not output:
            return c
        else:
            assert c.return_code == 0
            return c.out.strip()

    def _sanity_check(self):
        self._version = semver.parse(self.tf("--version").split()[1][1:])
