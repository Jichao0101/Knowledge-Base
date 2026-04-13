#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


MIGRATION_ITEMS = [
    "AGENTS.md",
    "01_Knowledge/Agent Workflow",
    ".codex/agents",
    "logs",
    "02_Projects/Agent Workflow",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate bundled Agent Workflow three-side scaffolds into a target knowledge base."
    )
    parser.add_argument("--target", required=True, help="Target knowledge-base root path")
    parser.add_argument(
        "--source",
        default=None,
        help="Optional source repo root. Defaults to the plugin's bundled payload.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned file operations without writing anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target files and directories.",
    )
    return parser.parse_args()


def bundled_payload_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1] / "payload"


def ensure_safe_target(target: Path, source: Path) -> None:
    if target.resolve() == source.resolve():
        raise ValueError("Target root must be different from source root.")


def ensure_source_ready(source: Path) -> None:
    missing_items = [item for item in MIGRATION_ITEMS if not (source / item).exists()]
    if missing_items:
        formatted = ", ".join(missing_items)
        raise ValueError(
            f"Source root is incomplete: {source}. Missing migration items: {formatted}"
        )


def remove_existing(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def copy_item(src: Path, dst: Path, force: bool, dry_run: bool) -> str:
    if not src.exists():
        return f"SKIP missing source: {src}"

    if dst.exists():
        if not force:
            return f"SKIP exists: {dst}"
        if not dry_run:
            remove_existing(dst)
        return f"OVERWRITE {src} -> {dst}"

    return f"COPY {src} -> {dst}"


def perform_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def main() -> None:
    args = parse_args()
    source_root = (
        Path(args.source).expanduser().resolve()
        if args.source
        else bundled_payload_root_from_script().resolve()
    )
    target_root = Path(args.target).expanduser().resolve()

    ensure_safe_target(target_root, source_root)
    ensure_source_ready(source_root)

    operations: list[tuple[Path, Path, str]] = []
    for item in MIGRATION_ITEMS:
        src = source_root / item
        dst = target_root / item
        status = copy_item(src, dst, args.force, args.dry_run)
        operations.append((src, dst, status))

    print("Agent Workflow migration plan:")
    for _, _, status in operations:
        print(f"- {status}")

    if args.dry_run:
        print("Dry run only; no files written.")
        return

    for src, dst, status in operations:
        if status.startswith(("COPY", "OVERWRITE")):
            perform_copy(src, dst)

    print("Migration completed.")


if __name__ == "__main__":
    main()
