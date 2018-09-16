import os

TERRAFORM_EXE = "terraform"
TERRAPYN_TIMEOUT = 60 * 5


def evaluate(*, environ=os.environ, executable=TERRAFORM_EXE):
    """Evaluate the (potentially) isolated runtime environment variables."""
    # If False was passed to environ...
    if not environ:
        environ = {}

    d = environ.copy()
    d.update(
        {
            "TERRAFORM_PATH": environ.get("TERRAFORM_PATH", executable),
            "TERRAPYN_TIMEOUT": environ.get("TERRAPYN_TIMEOUT", TERRAPYN_TIMEOUT),
        }
    )
    return d
