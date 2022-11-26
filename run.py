import logging
from sys import stdin, stdout, argv
from pathlib import Path
import subprocess
import time
import os
import sys

from src.containers.container_manager_client import ContainerManagerClient
from src.system.syspath import get_server_addr_file
from src.cli.cli import JabberwockyCLI


def main():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not get_server_addr_file().is_file():
        logger.debug("Starting server...")
        if os.name == "nt":
            if getattr(sys, 'frozen', False):
                target = Path(sys.executable).parent.parent / "server" / "server.exe"
            else:
                target = "python server.py"

            subprocess.Popen(
                str(target),
                shell=True,
                stdin=None,
                stdout=None,
                stderr=None,
                creationflags=subprocess.DETACHED_PROCESS,
            )
        else:
            raise NotImplementedError(os.name)
            # subprocess.Popen(
            #     "python3 server.py",
            #     shell=True,
            #     stdin=None,
            #     stdout=None,
            #     stderr=None,
            # )
        time.sleep(1)

    cli = JabberwockyCLI(stdin, stdout)
    cli.container_manager = ContainerManagerClient()
    inp = " ".join(argv[1:])
    cli.parse_cmd(inp)


if __name__ == "__main__":
    main()
