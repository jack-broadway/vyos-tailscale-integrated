#!/usr/bin/env python3
from cProfile import run
from pathlib import Path
import shutil
import subprocess

VYOS_GIT = "https://github.com/vyos/vyos-1x.git"
VYOS_BRANCH = "equuleus"
VYOS_BUILD_GIT = "https://github.com/vyos/vyos-build.git"
VYOS_BUILD_BRANCH = "equuleus"

VENDOR_DIR = Path("vendor")
shutil.rmtree(VENDOR_DIR, ignore_errors=True)
VENDOR_DIR.mkdir()


def run_command_in_build_container(cmd, working_dir: Path, branch=VYOS_BUILD_BRANCH):
    if isinstance(cmd, str):
        cmd = cmd.split(" ")

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-it",
            "--privileged",
            "-v",
            f"{working_dir.resolve()}:/vyos",
            "-w",
            "/vyos",
            f"vyos/vyos-build:{branch}",
        ] + cmd
    )


# Clone repos and merge filesystems
for repo, branch in [(VYOS_GIT, VYOS_BRANCH), (VYOS_BUILD_GIT, VYOS_BUILD_BRANCH)]:
    repo_path = VENDOR_DIR / Path(repo).stem
    subprocess.run(
        [
            "git",
            "clone",
            repo,
            "-b",
            branch,
            "--single-branch",
            str(repo_path),
        ]
    )
    subprocess.run(["rsync", "-a", f"override/{Path(repo).stem}", VENDOR_DIR])

work_dir = VENDOR_DIR / "vyos-1x"
subprocess.run(
    [
        "docker",
        "run",
        "--rm",
        "-it",
        "--privileged",
        "--sysctl",
        "net.ipv6.conf.lo.disable_ipv6=0",
        "-v",
        f"{VENDOR_DIR.resolve()}:/vyos",
        "-w",
        "/vyos/vyos-1x",
        f"vyos/vyos-build:{branch}",
        "dpkg-buildpackage",
        "-uc",
        "-us",
        "-tc",
        "-b",
    ],
    cwd=work_dir,
)

vyos_deb = next(VENDOR_DIR.glob("vyos-1x_*.deb"))
shutil.copy(vyos_deb, VENDOR_DIR / "vyos-build" / "packages")

# Configure and build vyos 
cmd = ["./configure", "--architecture", "amd64", "--custom-apt-key", "./tailscale.gpg", "--custom-apt-entry", "deb https://pkgs.tailscale.com/stable/debian buster main", "--custom-package", "tailscale", "--build-comment", "VyOS with Tailscale", "--build-type", "production", "--version", "1.3-equuleus-tailscale"]
run_command_in_build_container(cmd, working_dir=VENDOR_DIR/"vyos-build")

cmd = ["sudo", "make", "iso"]
run_command_in_build_container(cmd, working_dir=VENDOR_DIR/"vyos-build")