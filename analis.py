import os
import sys
import json
import shutil
import argparse
import subprocess
from typing import Optional, List, Tuple

#!/usr/bin/env python3
"""
analis.py - small helper to detect and inspect Anaconda/Conda environments.

Usage examples:
    python analis.py           # show status summary
    python analis.py list      # list installed packages
    python analis.py export -o env.yml   # export environment (conda preferred, pip fallback)
"""



def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
        try:
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                return p.returncode, p.stdout.strip(), p.stderr.strip()
        except FileNotFoundError:
                return 127, "", f"executable not found: {cmd[0]}"


def conda_available() -> bool:
        return shutil.which("conda") is not None


def get_conda_version() -> Optional[str]:
        code, out, err = run_cmd(["conda", "--version"])
        if code == 0 and out:
                return out.strip()
        return None


def get_conda_info() -> Optional[dict]:
        code, out, err = run_cmd(["conda", "info", "--json"])
        if code == 0 and out:
                try:
                        return json.loads(out)
                except json.JSONDecodeError:
                        return None
        return None


def current_env_name() -> Optional[str]:
        # Prefer environment variable
        env = os.environ.get("CONDA_DEFAULT_ENV")
        if env:
                return env
        # Try conda info
        info = get_conda_info()
        if info:
                name = info.get("active_prefix_name") or info.get("default_prefix_name")
                if name:
                        return name
                # if active_prefix provided, derive name from prefixes list
                active_prefix = info.get("active_prefix")
                prefixes = info.get("envs", [])
                if active_prefix and prefixes:
                        for p in prefixes:
                                if os.path.normcase(p) == os.path.normcase(active_prefix):
                                        return os.path.basename(p)
        # Fallback: if CONDA_PREFIX present, use basename
        prefix = os.environ.get("CONDA_PREFIX")
        if prefix:
                return os.path.basename(prefix)
        return None


def list_conda_packages() -> Optional[List[str]]:
        code, out, err = run_cmd(["conda", "list", "--json"])
        if code != 0 or not out:
                return None
        try:
                items = json.loads(out)
                return [f"{it.get('name')}=={it.get('version')}" for it in items]
        except json.JSONDecodeError:
                return None


def list_pip_packages() -> List[str]:
        code, out, err = run_cmd([sys.executable, "-m", "pip", "freeze"])
        if code == 0:
                return [line for line in out.splitlines() if line.strip()]
        return []


def export_conda_env(output_path: str, name: Optional[str] = None) -> bool:
        cmd = ["conda", "env", "export", "--no-builds", "-f", output_path]
        if name:
                cmd = ["conda", "env", "export", "--name", name, "--no-builds", "-f", output_path]
        code, out, err = run_cmd(cmd)
        return code == 0


def export_pip_requirements(output_path: str) -> bool:
        code, out, err = run_cmd([sys.executable, "-m", "pip", "freeze"])
        if code != 0:
                return False
        try:
                with open(output_path, "w", encoding="utf-8") as f:
                        f.write(out)
                return True
        except OSError:
                return False


def print_status():
        print("Conda available:", "yes" if conda_available() else "no")
        if conda_available():
                print("Conda version:", get_conda_version() or "unknown")
        print("Python:", sys.executable)
        print("Python version:", sys.version.splitlines()[0])
        env = current_env_name()
        print("Active conda env:", env if env else "(none detected)")
        prefix = os.environ.get("CONDA_PREFIX")
        if prefix:
                print("Conda prefix:", prefix)


def cmd_list():
        if conda_available():
                pkgs = list_conda_packages()
                if pkgs is not None:
                        for p in pkgs:
                                print(p)
                        return
        # fallback to pip
        for p in list_pip_packages():
                print(p)


def cmd_export(path: str):
        if conda_available():
                name = current_env_name()
                ok = export_conda_env(path, name)
                if ok:
                        print(f"Exported conda env to {path}")
                        return
                # try without name
                ok2 = export_conda_env(path, None)
                if ok2:
                        print(f"Exported conda env to {path}")
                        return
        # fallback to pip freeze
        if export_pip_requirements(path):
                print(f"Exported pip requirements to {path}")
        else:
                print("Export failed.")


def main(argv=None):
        parser = argparse.ArgumentParser(description="Simple Anaconda/Conda helper")
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("status", help="Show conda/python status")
        sub.add_parser("list", help="List installed packages (conda preferred)")
        ex = sub.add_parser("export", help="Export environment")
        ex.add_argument("-o", "--output", default="environment.yml", help="Output path (default: environment.yml)")
        args = parser.parse_args(argv)

        cmd = args.command or "status"
        if cmd == "status":
                print_status()
        elif cmd == "list":
                cmd_list()
        elif cmd == "export":
                cmd_export(args.output)
        else:
                parser.print_help()


if __name__ == "__main__":
        main()