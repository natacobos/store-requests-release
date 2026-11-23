"""`python3 check/check.py`: one line per task, for the interviewer. Do not edit anything in check/.
Standard library only."""

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_SECRET = "demo-secret-7Hk2-do-not-use"
EXPECTED = {
    "dev": ("https://servicedesk-test.example.com/api", "c0nn-dev-4711"),
    "tst": ("https://servicedesk-test.example.com/api", "c0nn-tst-5822"),
    "prd": ("https://servicedesk.example.com/api", "c0nn-prd-6933"),
}


def read(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def stages(yml):
    """Split the pipeline into stage blocks by the '- stage: NAME' lines."""
    lines = [l for l in yml.splitlines() if not l.lstrip().startswith("#")]
    found, name, block = {}, None, []
    indent = None
    for line in lines:
        m = re.match(r"^(\s*)- stage:\s*(\S+)", line)
        if m and (indent is None or len(m.group(1)) == indent):
            if name:
                found[name.upper()] = "\n".join(block)
            indent, name, block = len(m.group(1)), m.group(2), [line]
        elif name:
            block.append(line)
    if name:
        found[name.upper()] = "\n".join(block)
    return found


def settings(env):
    try:
        data = json.loads(read(f"settings/{env}.json"))
        url = next(v["Value"] for v in data["EnvironmentVariables"] if v["SchemaName"] == "sr_ServiceDeskUrl")
        conn = next(c["ConnectionId"] for c in data["ConnectionReferences"] if c["LogicalName"] == "sr_ServiceDeskConnection")
        return url, conn
    except (ValueError, KeyError, StopIteration, TypeError):
        return None


yml = read("pipelines/release.yml")
st = stages(yml)
prd = st.get("PRD", "")

# Task 1: approval before production
t1a = bool(re.search(r"^\s*-\s*deployment:", prd, re.M)) and bool(
    re.search(r"environment:\s*(?:\n\s*name:\s*)?['\"]?prd['\"]?\s*$", prd, re.M | re.I))
depends = re.search(r"dependsOn:\s*(.*(?:\n\s*-\s*.*)*)", prd)
cond = re.search(r"^\s*condition:\s*(.+)$", prd, re.M)
t1b = bool(depends and re.search(r"\bTST\b", depends.group(1), re.I)) and not (
    cond and re.search(r"always\(\)|failed\(\)|succeededOrFailed\(\)", cond.group(1)))

# Task 2: no secret in the repository; read from Key Vault; one secret per environment
repo_text = ""
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in (".git", "check")]
    for f in files:
        try:
            with open(os.path.join(base, f), encoding="utf-8") as fh:
                repo_text += fh.read()
        except (OSError, UnicodeDecodeError):
            pass
t2a = OLD_SECRET not in repo_text
t2b = bool(re.search(r"AzureKeyVault@\d", yml)) or bool(re.search(r"^\s*-\s*group:\s*\S+", yml, re.M))
t2c = all(
    re.search(rf"pp-secret-{env}", st.get(env.upper(), ""), re.I)
    and re.search(r"pac auth create[^\n]*--clientSecret\s+\$\(", st.get(env.upper(), ""))
    for env in ("dev", "tst", "prd"))

# Task 3: TST settings, without breaking DEV and PRD
values = {env: settings(env) for env in EXPECTED}
others_ok = values["dev"] == EXPECTED["dev"] and values["prd"] == EXPECTED["prd"]
t3a = others_ok and bool(values["tst"]) and values["tst"][0] == EXPECTED["tst"][0]
t3b = others_ok and bool(values["tst"]) and values["tst"][1] == EXPECTED["tst"][1]

h = hashlib.sha256()
for f in sorted(os.listdir(os.path.join(ROOT, "check"))):
    p = os.path.join(ROOT, "check", f)
    if os.path.isfile(p) and f.endswith(".py"):
        h.update(f.encode())
        with open(p, "rb") as fh:
            h.update(fh.read())


def line(label, text):
    print(label.ljust(24, ".") + " " + text)


mark = lambda ok: "✓" if ok else "✗"
print("\nStore Requests release pipeline — check\n")
line("Stages found", ", ".join(st) or "none ✗")
line("T1 Approval before PRD", f"{t1a + t1b}/2  deployment job on 'prd' {mark(t1a)}  runs only after TST succeeds {mark(t1b)}")
line("T2 Secrets", f"{t2a + t2b + t2c}/3  no secret in the repo {mark(t2a)}  read from Key Vault {mark(t2b)}  "
                   f"own secret per environment {mark(t2c)}")
line("T3 TST settings", f"{t3a + t3b}/2  service desk address {mark(t3a)}  connection {mark(t3b)}"
                        + ("" if others_ok else "  (DEV or PRD settings were changed ✗)"))
line("Check files", h.hexdigest()[:8])
print("")
