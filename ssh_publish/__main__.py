import os
from argparse import ArgumentParser
from pathlib import Path

from paramiko import AutoAddPolicy, SSHClient
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "pkg_index_host", help="Host of the package index, eg. 198.168.100.10"
    )
    parser.add_argument(
        "directory",
        help="Directory path to upload the package, eg. packages/my-package",
    )
    args = parser.parse_args()

    wheels = list(Path("dist").glob("*.whl"))
    if not wheels:
        print("No wheels found in dist folder.")
        return
    latest_wheel = max(wheels, key=os.path.getmtime)
    print(f"package: {latest_wheel.name}")
    print("connecting to ssh host...")
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        if "@" in args.pkg_index_host:
            user, host = args.pkg_index_host.split("@")
            ssh.connect(hostname=host, username=user)
        else:
            ssh.connect(args.pkg_index_host)
        print("checking if file already exists...")
        _, stdout, _ = ssh.exec_command(
            f"ls {args.directory}/{latest_wheel.name}", timeout=30
        )
        if stdout.read():
            raise Exception(f"Package {latest_wheel.name} already exists.")
        print("creating directories...")
        ssh.exec_command(f"mkdir -p {args.directory}", timeout=30)
        with ssh.open_sftp() as sftp:
            remote_path = args.directory + "/" + latest_wheel.name
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("uploading", total=latest_wheel.stat().st_size)

                def callback(transferred: int, total: int) -> None:
                    progress.update(task, completed=transferred)

                sftp.put(latest_wheel, remote_path, callback=callback)
        print("done.")


if __name__ == "__main__":
    main()
