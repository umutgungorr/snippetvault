"""Cross-platform zero-dependency clipboard helper."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys


def copy_to_clipboard(text: str) -> bool:
    """Copy text to operating system clipboard without external dependencies."""
    system = platform.system().lower()

    try:
        if system == "windows":
            # Use clip.exe on Windows
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        elif system == "darwin":
            # Use pbcopy on macOS
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        else:
            # Linux / Unix
            for tool in ["wl-copy", "xclip", "xsel"]:
                if shutil.which(tool):
                    args = [tool]
                    if tool == "xclip":
                        args.extend(["-selection", "clipboard"])
                    elif tool == "xsel":
                        args.extend(["--clipboard", "--input"])
                    p = subprocess.Popen(args, stdin=subprocess.PIPE)
                    p.communicate(text.encode("utf-8"))
                    return p.returncode == 0
    except Exception:
        pass

    return False
