import sys
import os
from pathlib import Path
import subprocess as sp
from src.system.syspath import get_container_id_rsa

def filezilla(user: str, pswd: str, host: str, port: str):
    args = f"sftp://{user}:{pswd}@{host}:{port}"

    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent.parent / "contrib" / "filezilla"
    else:
        base = Path(__file__).parent.parent.parent / "contrib" / "filezilla"

    if sys.platform == "win32":
        sp.Popen([base / "filezilla.exe", args], creationflags=sp.DETACHED_PROCESS)
    elif sys.platform == "linux":
        sp.Popen([base / "bin" / "filezilla", args])
    elif sys.platform == "darwin":
        sp.Popen([
            Path("/usr/bin/open"),
            base / "FileZilla.app",
            "--args",
            args
        ])
    else:
        raise RuntimeError(f"Unknown Platform {sys.platform}")

def sftp(user: str, pswd: str, host: str, port: str, cname: str):
    args = [
        "C:\\Windows\\System32\\OpenSSH\\sftp.exe" if sys.platform == "win32" else "/usr/bin/sftp",
        "-oStrictHostKeyChecking=no",
        "-oLogLevel=ERROR",
        "-oPasswordAuthentication=no",
        "-i{}".format(get_container_id_rsa(cname)),
        "-P{}".format(port),
        "{}@{}".format(user, host)
    ]

    if sys.platform == "darwin":
        os.system(" ".join(args)) # sp.run is buggy on macOS
    else:
        sp.run(args, shell=True)
