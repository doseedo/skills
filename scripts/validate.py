#!/usr/bin/env python3
"""Validate the skills pack — the same checks CI runs, no dependencies.

  - every doseedo-*/SKILL.md has YAML frontmatter with name == folder,
    a version equal to VERSION, and a description that says when to use
    the skill ("Use when") and when not to ("NOT for"), ≤ 1024 chars
  - every plugin manifest's version equals VERSION
  - .claude-plugin/marketplace.json lists every skill folder
  - every references/*.md a SKILL.md links exists, and no reference file is
    orphaned
  - no parent-directory (../) paths: an installed skill must be self-contained

Exit 1 on the first class of failure, after printing every finding.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def err(msg):
    errors.append(msg)
    print(f"✗ {msg}")


def parse_frontmatter(text):
    """A tiny YAML subset: `key: value` and `key: |` block scalars."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm, cur, buf = {}, None, []
    for line in m.group(1).split("\n"):
        if cur and (line.startswith("  ") or line == ""):
            buf.append(line.strip())
            continue
        if cur:
            fm[cur] = " ".join(x for x in buf if x)
            cur, buf = None, []
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not km:
            continue
        k, v = km.group(1), km.group(2).strip()
        if v == "|" or v == ">":
            cur = k
        else:
            fm[k] = v.strip('"').strip("'")
    if cur:
        fm[cur] = " ".join(x for x in buf if x)
    return fm


def main():
    version = open(os.path.join(ROOT, "VERSION")).read().strip()
    skills = sorted(d for d in os.listdir(ROOT) if d.startswith("doseedo-") and os.path.isdir(os.path.join(ROOT, d)))
    if not skills:
        err("no doseedo-* skill folders found")

    for s in skills:
        p = os.path.join(ROOT, s, "SKILL.md")
        if not os.path.exists(p):
            err(f"{s}/SKILL.md missing")
            continue
        text = open(p).read()
        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{p}: no YAML frontmatter")
            continue
        if fm.get("name") != s:
            err(f"{p}: name '{fm.get('name')}' != folder '{s}'")
        if fm.get("version") != version:
            err(f"{p}: version '{fm.get('version')}' != VERSION {version}")
        desc = fm.get("description", "")
        if not desc:
            err(f"{p}: description missing")
        if len(desc) > 1024:
            err(f"{p}: description is {len(desc)} chars (> 1024)")
        if "Use when" not in desc:
            err(f"{p}: description lacks 'Use when' trigger phrases")
        if "NOT for" not in desc:
            err(f"{p}: description lacks a 'NOT for' boundary")
        if re.search(r"(^|[^./])\.\./", text):
            err(f"{p}: contains a parent-dir (../) reference")
        refdir = os.path.join(ROOT, s, "references")
        linked = set(re.findall(r"references/[A-Za-z0-9_./-]+\.md", text))
        for ref in linked:
            if not os.path.exists(os.path.join(ROOT, s, ref)):
                err(f"{p}: links {ref} which does not exist")
        if os.path.isdir(refdir):
            for f in sorted(os.listdir(refdir)):
                if f.endswith(".md") and f"references/{f}" not in linked:
                    err(f"{s}/references/{f}: orphaned (not linked from SKILL.md)")
                rt = open(os.path.join(refdir, f)).read()
                if re.search(r"(^|[^./])\.\./\.\./", rt):
                    err(f"{s}/references/{f}: contains ../../")
        if not errors or all(s not in e for e in errors):
            print(f"✓ {s} (v{fm.get('version')})")

    for mf in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        fp = os.path.join(ROOT, mf)
        if not os.path.exists(fp):
            err(f"{mf} missing")
            continue
        v = json.load(open(fp)).get("version")
        if v != version:
            err(f"{mf}: version {v} != VERSION {version}")
    mp = os.path.join(ROOT, ".claude-plugin/marketplace.json")
    if os.path.exists(mp):
        m = json.load(open(mp))
        plug = m["plugins"][0]
        if plug.get("version") != version:
            err(f"marketplace.json: plugins[0].version {plug.get('version')} != VERSION {version}")
        listed = {sk["path"] for sk in plug.get("skills", [])}
        for s in skills:
            if s not in listed:
                err(f"marketplace.json does not list {s}")
        for path in listed:
            if path not in skills:
                err(f"marketplace.json lists {path} which is not a skill folder")
    else:
        err(".claude-plugin/marketplace.json missing")

    if errors:
        print(f"\n{len(errors)} problem(s)")
        sys.exit(1)
    print(f"\n✓ skills pack v{version}: {len(skills)} skills, manifests in sync")


if __name__ == "__main__":
    main()
