#!/usr/bin/env python3
"""Quét cấu hình global của OpenCode và sinh data.js cho trang xem read-only.

Chạy: python3 build.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CONFIG = HOME / ".config/opencode"
SKILLS_DIR = CONFIG / "skills"
COMMANDS_DIR = CONFIG / "commands"
CLAUDE_SYNCED = HOME / ".claude/skills/synced"
OUT = Path(__file__).resolve().parent / "data.js"

DOMAINS = {
    "Tài liệu": {
        "docx", "pdf", "pptx", "xlsx", "doc-coauthoring", "writing-guidelines",
    },
    "Web & UI": {
        "frontend-design", "web-design-guidelines", "web-artifacts-builder",
        "canvas-design", "algorithmic-art", "theme-factory", "composition-patterns",
        "react-best-practices", "react-view-transitions",
    },
    "Animation & Video": {"motion"},
    "Kỹ thuật": {
        "ponytail", "graphify", "mcp-builder", "skill-creator",
        "free-only-dependencies",
    },
    "Kiểm thử": {"playwright", "webapp-testing", "screenshot"},
    "Bảo mật": {"security-best-practices", "security-threat-model"},
}

SOURCE_LABELS = [
    ("watch2learn/.agents", "watch2learn", "watch2learn/.agents/skills"),
    ("anthropics--skills", "anthropics/skills", "20-repo-generate-video/repos/anthropics--skills"),
    ("vercel-labs--agent-skills", "vercel-labs/agent-skills", "20-repo-generate-video/repos/vercel-labs--agent-skills"),
    ("20-repo-generate-video/skills", "20-repo-generate-video", "20-repo-generate-video/skills"),
]


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    """Đọc YAML frontmatter đơn giản (key, folded/normal value) + phần body."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}, ""

    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", text, re.DOTALL)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    key = None
    style = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal key, style, buffer
        if key is not None:
            value = "\n".join(buffer).strip() if style == "|" else " ".join(
                part.strip() for part in buffer
            ).strip()
            meta[key] = value
        key, style, buffer = None, None, []

    for raw in match.group(1).splitlines():
        if not raw.strip():
            if key:
                buffer.append("")
            continue
        if raw.startswith((" ", "\t")):
            if key:
                buffer.append(raw.strip())
            continue
        if ":" not in raw:
            continue
        flush()
        name, value = raw.split(":", 1)
        name, value = name.strip(), value.strip()
        key = name
        if value in (">", "|", ">-", "|-"):
            style = value[0]
        elif value:
            meta[name] = value.strip("'\"")
            key = None
    flush()

    return meta, text[match.end():].strip()


def source_of(real_path: Path) -> tuple[str, str]:
    raw = str(real_path)
    for needle, label, rel in SOURCE_LABELS:
        if needle in raw:
            root = raw.split(needle, 1)[0].rstrip("/")
            return label, f"{root}/{rel}"
    return "Bản copy nội bộ", str(CONFIG / "skills")


def domain_of(name: str) -> str:
    if name.startswith(("gsap-", "remotion-")):
        return "Animation & Video"
    for domain, names in DOMAINS.items():
        if name in names:
            return domain
    return "Khác"


def count_files(path: Path) -> int:
    total = 0
    try:
        for _, dirs, files in os.walk(path, followlinks=True):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]
            total += len(files)
            if total > 500:
                break
    except OSError:
        pass
    return total


def api_get(endpoint: str):
    try:
        proc = subprocess.run(
            ["opencode", "api", "get", endpoint],
            capture_output=True, text=True, timeout=20,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout).get("data")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def collect_skills() -> tuple[list[dict], int]:
    skills: list[dict] = []
    broken = 0

    for entry in sorted(SKILLS_DIR.iterdir()):
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            broken += 1
            continue
        meta, _ = parse_frontmatter(skill_md)
        real = entry.resolve()
        source, source_path = source_of(real)
        name = meta.get("name") or entry.name
        skills.append({
            "name": name,
            "description": meta.get("description", ""),
            "path": str(skill_md),
            "realPath": str(real),
            "source": source,
            "sourcePath": source_path,
            "kind": "copy" if not entry.is_symlink() else "symlink",
            "domain": domain_of(entry.name),
            "files": count_files(real),
            "license": meta.get("license", ""),
            "scope": "global",
        })

    api_skills = api_get("/api/skill")
    if api_skills is not None:
        known = {s["name"] for s in skills}
        for item in api_skills:
            path = item.get("path", "")
            if path.startswith("skill://"):
                name = item.get("id", "")
                if name in known:
                    continue
                skills.append({
                    "name": name,
                    "description": item.get("description", ""),
                    "path": path,
                    "realPath": "",
                    "source": "OpenCode built-in",
                    "sourcePath": "",
                    "kind": "builtin",
                    "domain": domain_of(name),
                    "files": 0,
                    "license": "",
                    "scope": "builtin",
                })
            elif ".claude/skills" in path:
                name = item.get("id", "")
                if name in known:
                    continue
                skill_dir = Path(path).parent
                skills.append({
                    "name": name,
                    "description": item.get("description", ""),
                    "path": path,
                    "realPath": str(skill_dir),
                    "source": "Claude synced",
                    "sourcePath": str(CLAUDE_SYNCED),
                    "kind": "synced",
                    "domain": domain_of(name),
                    "files": count_files(skill_dir) if skill_dir.exists() else 0,
                    "license": "",
                    "scope": "synced",
                })
    else:
        if CLAUDE_SYNCED.exists():
            for skill_md in sorted(CLAUDE_SYNCED.glob("*/SKILL.md")):
                meta, _ = parse_frontmatter(skill_md)
                name = meta.get("name") or skill_md.parent.name
                skills.append({
                    "name": name,
                    "description": meta.get("description", ""),
                    "path": str(skill_md),
                    "realPath": str(skill_md.parent),
                    "source": "Claude synced",
                    "sourcePath": str(CLAUDE_SYNCED),
                    "kind": "synced",
                    "domain": domain_of(name),
                    "files": count_files(skill_md.parent),
                    "license": "",
                    "scope": "synced",
                })

    skills.sort(key=lambda s: (s["name"].lower()))
    return skills, broken


def collect_commands() -> list[dict]:
    commands = []
    for md in sorted(COMMANDS_DIR.glob("*.md")):
        meta, body = parse_frontmatter(md)
        commands.append({
            "name": md.stem,
            "description": meta.get("description", ""),
            "agent": meta.get("agent", ""),
            "path": str(md),
            "body": body,
            "builtin": False,
        })

    api_commands = api_get("/api/command") or []
    known = {c["name"] for c in commands}
    for item in api_commands:
        name = item.get("name", "")
        if name and name not in known:
            commands.append({
                "name": name,
                "description": item.get("description", ""),
                "agent": "",
                "path": "",
                "body": "",
                "builtin": True,
            })
    return commands


def collect_config() -> dict:
    cfg = {}
    try:
        cfg = json.loads((CONFIG / "opencode.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass

    agent_files = []
    for folder in ("agent", "agents"):
        base = CONFIG / folder
        if base.exists():
            agent_files.extend(str(p) for p in sorted(base.glob("*.md")))

    plugins = []
    for folder in ("plugin", "plugins"):
        base = CONFIG / folder
        if base.exists():
            plugins.extend(str(p.name) for p in sorted(base.iterdir()))

    permissions = [
        {
            "action": item.get("action", ""),
            "resource": item.get("resource", ""),
            "effect": item.get("effect", ""),
        }
        for item in cfg.get("permissions", [])
        if isinstance(item, dict)
    ]

    return {
        "path": str(CONFIG),
        "todo": bool(cfg.get("experimental", {}).get("todo")),
        "permissions": permissions,
        "mcp": sorted(cfg.get("mcp", {}).keys()) if isinstance(cfg.get("mcp"), dict) else [],
        "pluginCount": len(plugins),
        "agents": agent_files,
        "commandsDir": str(COMMANDS_DIR),
        "skillsDir": str(SKILLS_DIR),
        "linkScript": str(CONFIG / "scripts/link-skills.sh"),
    }


def read_doc(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def build() -> dict:
    skills, broken = collect_skills()
    commands = collect_commands()
    config = collect_config()

    global_skills = [s for s in skills if s["scope"] == "global"]
    builtin_skills = [s for s in skills if s["scope"] == "builtin"]
    synced_skills = [s for s in skills if s["scope"] == "synced"]
    custom_commands = [c for c in commands if not c["builtin"]]

    source_map: dict[str, dict] = {}
    for skill in skills:
        key = skill["source"]
        bucket = source_map.setdefault(key, {
            "name": key,
            "path": skill["sourcePath"],
            "count": 0,
        })
        bucket["count"] += 1

    domain_counts: dict[str, int] = {}
    for skill in skills:
        domain_counts[skill["domain"]] = domain_counts.get(skill["domain"], 0) + 1

    return {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "totals": {
            "skills": len(skills),
            "globalSkills": len(global_skills),
            "builtinSkills": len(builtin_skills),
            "syncedSkills": len(synced_skills),
            "commands": len(custom_commands),
            "builtinCommands": len(commands) - len(custom_commands),
            "agents": len(config["agents"]),
            "mcp": len(config["mcp"]),
            "sources": len(source_map),
            "brokenLinks": broken,
        },
        "skills": skills,
        "commands": commands,
        "domains": domain_counts,
        "sources": sorted(source_map.values(), key=lambda s: (-s["count"], s["name"])),
        "config": config,
        "docs": {
            "rules": read_doc(CONFIG / "AGENTS.md"),
            "workflow": read_doc(CONFIG / "README-workflow.md"),
            "skillSources": read_doc(CONFIG / "README-skills.md"),
        },
    }


def main() -> None:
    data = build()
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    OUT.write_text(
        "/* Sinh tự động bởi build.py — đừng sửa tay. */\n"
        f"window.AGENT_DATA = {payload};\n",
        encoding="utf-8",
    )
    t = data["totals"]
    print(
        f"Đã ghi {OUT.name}: {t['skills']} skill "
        f"({t['globalSkills']} global, {t['builtinSkills']} built-in, {t['syncedSkills']} synced), "
        f"{t['commands']} lệnh custom, {t['brokenLinks']} symlink gãy."
    )


if __name__ == "__main__":
    main()
