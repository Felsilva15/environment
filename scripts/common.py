"""Small shared primitives; native installation remains the adapter's responsibility."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class EnvironmentError(Exception):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".write-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def inside(root, relative):
    root = Path(root).resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise EnvironmentError(f"Path escapes repository: {relative}")
    return candidate


def source_files(root):
    """Ignore installed dependencies, but never follow source symlinks."""
    root = Path(root)
    if root.is_symlink():
        raise EnvironmentError(f"Source must not be a symlink: {root}")
    if not root.is_dir():
        raise EnvironmentError(f"Missing source directory: {root}")
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(p in {"node_modules", ".git", "__pycache__"} for p in rel.parts):
            continue
        if path.is_symlink():
            raise EnvironmentError(f"Source symlink is not portable: {path}")
        if path.is_file():
            if (path.name == ".env" or path.name.startswith(".env.") and path.name != ".env.example"
                    or path.name in {"auth.json", "credentials.json"}
                    or path.suffix in {".pem", ".key"}):
                raise EnvironmentError(f"Credential-like file must remain outside portable source: {path}")
            yield rel, path


def digest(root):
    result = hashlib.sha256()
    for relative, path in source_files(root):
        result.update(relative.as_posix().encode() + b"\0")
        result.update(path.read_bytes() + b"\0")
    return result.hexdigest()


def copy_source(source, target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for relative, path in source_files(source):
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def run(command, cwd=None, capture=True):
    result = subprocess.run(
        [str(x) for x in command], cwd=cwd, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    if result.returncode:
        # Avoid dumping auth output or credentials into generated state/report files.
        raise EnvironmentError(f"Command failed ({result.returncode}): {command[0]} {' '.join(map(str, command[1:3]))}")
    return result.stdout if capture else ""


def managed_status(source, target, previous=None):
    desired = digest(source)
    target = Path(target)
    if target.is_symlink():
        return "conflict", desired
    if not target.exists():
        return "install", desired
    if not target.is_dir():
        return "conflict", desired
    current = digest(target)
    if current == desired:
        return "ok", desired
    if previous and current == previous:
        return "update", desired
    return "conflict", desired


def install_tree(source, target, backups):
    """Stage on the target filesystem; preserve the old tree before replacing it."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".environment-", dir=target.parent))
    try:
        copy_source(source, stage)
        if target.exists() or target.is_symlink():
            backups = Path(backups)
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups / target.name
            if backup.exists():
                raise EnvironmentError(f"Backup already exists: {backup}")
            shutil.move(str(target), str(backup))
        os.replace(stage, target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
