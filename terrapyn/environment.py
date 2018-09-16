import os

TERRAFORM_EXE = 'terraform'


def evaluate(environ=os.environ, executable=TERRAFORM_EXE):
    return {
        'TERRAFORM_PATH': environ.get('TERRAFORM_PATH', executable),
    }
