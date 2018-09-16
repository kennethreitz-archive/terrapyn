import os
import tempfile

import delegator

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


class TerraformInstance(BaseCommand):
    def __init__(self, *, environ=None):
        self.environ = environment.evaluate(environ=environ)
        self.version = None
        self.temp_dir = None

        self._sanity_check()
        self.setup()

    def __repr__(self):
        return f"<TerraformCommand version={self.version!r}>"

    def __enter__(self):
        if not self.temp_dir:
            self.setup()

    def __exit__(self, type, value, tb):
        self.cleanup()

    def setup(self):
        self.temp_dir = tempfile.mkdtemp(suffix="-terraform-plan", prefix="terrapyn-")

    def cleanup(self):
        if self.temp_dir:
            os.rmdir(self.temp_dir)
            self.temp_dir = None

    def _tf(self, *args, output=True):
        cmd = [self.environ["TERRAFORM_PATH"]] + list(args)
        c = delegator.run(cmd, timeout=self.environ["TERRAPYN_TIMEOUT"])
        if not output:
            return c
        else:
            assert c.return_code == 0
            return c.out.strip()

    def _sanity_check(self):
        self.version = self._tf("--version").split()[1][1:]
