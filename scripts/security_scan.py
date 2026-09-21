#!/usr/bin/env python3
"""Scan the worktree and Git history without printing possible secret values."""

from pathlib import Path
import re
import io
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SECRET_PATTERNS = {
    "private key": re.compile(rb"BEGIN [A-Z ]*PRIVATE KEY"),
    "credential assignment": re.compile(rb"(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*['\"][^'\"]{8,}", re.I),
    "GitHub token": re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "Netlify token": re.compile(rb"nfp_[A-Za-z0-9_-]{20,}"),
}
PRICE_PATTERN = re.compile(rb"\b(?:EUR|USD)\s*\d|\d[\d., ]*\s*(?:EUR\b|USD\b|\xe2\x82\xac)", re.I)
PRIVATE_EXTENSION = re.compile(r"\.(?:eml|pdf|pem|key|p12|pfx|env)$", re.I)


def scan(data, label, secrets, prices):
    if b"\0" in data[:8192] or len(data) > 2_000_000:
        return
    for kind, pattern in SECRET_PATTERNS.items():
        if pattern.search(data):
            secrets.add((kind, label))
    if PRICE_PATTERN.search(data):
        prices.add(label)


def main():
    secrets, prices, private = set(), set(), set()
    tracked = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    paths = {ROOT / name for name in tracked if name}
    paths.update((ROOT / "dist").rglob("*"))
    scanned = 0
    for path in paths:
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = str(path.relative_to(ROOT))
        if PRIVATE_EXTENSION.search(rel):
            private.add("worktree:" + rel)
        if path.stat().st_size <= 2_000_000:
            scan(path.read_bytes(), "worktree:" + rel, secrets, prices)
            scanned += 1

    objects = {}
    output = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT, text=True)
    for line in output.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            objects.setdefault(parts[0], parts[1])
    object_metadata = subprocess.check_output(["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"], cwd=ROOT, input="\n".join(objects) + "\n", text=True)
    sizes = {line.split()[0]: (line.split()[1], int(line.split()[2])) for line in object_metadata.splitlines()}
    eligible = []
    for sha, path in objects.items():
        if PRIVATE_EXTENSION.search(path):
            private.add("history:" + path)
        if sizes[sha][0] == "blob" and sizes[sha][1] <= 2_000_000:
            eligible.append(sha)
    history_text = len(eligible)
    payload = subprocess.check_output(["git", "cat-file", "--batch"], cwd=ROOT, input=("\n".join(eligible) + "\n").encode())
    stream = io.BytesIO(payload)
    for sha in eligible:
        header = stream.readline().decode().split()
        data = stream.read(int(header[2])); stream.read(1)
        scan(data, "history:" + objects[sha], secrets, prices)

    if secrets or prices or private:
        print("SECURITY SCAN FAILED")
        for kind, path in sorted(secrets):
            print(f"- possible {kind}: {path}")
        for path in sorted(prices):
            print(f"- possible numeric public price: {path}")
        for path in sorted(private):
            print(f"- private-document extension: {path}")
        raise SystemExit(1)
    print(f"PASS: {scanned} current/public files and {len(objects)} historical Git objects ({history_text} content-scanned blobs) contain no credential, private-document or numeric-price patterns.")


if __name__ == "__main__":
    main()
