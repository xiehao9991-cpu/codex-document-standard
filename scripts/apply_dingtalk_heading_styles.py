import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


STYLES = {
    "Title": {"size": 18, "color": "#2F75B5"},
    "h1": {"size": 14, "color": "#2F75B5"},
    "h2": {"size": 12.5, "color": "#2F75B5"},
    "h3": {"size": 11.5, "color": "#2F75B5"},
}


def run_dws(*args):
    result = subprocess.run(
        ["dws", *args, "--format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def read_jsonml(node_id, output_path):
    run_dws(
        "doc",
        "read",
        "--node",
        node_id,
        "--content-format",
        "jsonml",
        "--output",
        str(output_path),
    )
    return json.loads(output_path.read_text(encoding="utf-8"))["jsonml"]


def find_leaf(node):
    if not isinstance(node, list):
        return None
    if len(node) >= 2 and node[0] == "span" and isinstance(node[1], dict):
        if node[1].get("data-type") == "leaf":
            return node[1]
    for child in node[2:]:
        found = find_leaf(child)
        if found is not None:
            return found
    return None


def style_key(block):
    if not isinstance(block, list) or len(block) < 2 or not isinstance(block[1], dict):
        return None
    if block[0] == "p" and block[1].get("styleId") == "Title":
        return "Title"
    if block[0] in {"h1", "h2", "h3"}:
        return block[0]
    return None


def apply_styles(node_id, root):
    targets = []
    for block in root[2:]:
        key = style_key(block)
        if key is None:
            continue
        attrs = block[1]
        leaf = find_leaf(block)
        if leaf is None:
            raise RuntimeError(f"No text leaf found for block {attrs.get('uuid')}")
        spec = STYLES[key]
        leaf.update(
            {
                "bold": True,
                "fonts": {
                    "ascii": "Aptos Display",
                    "eastAsia": "Microsoft YaHei",
                    "hAnsi": "Aptos Display",
                },
                "sz": spec["size"],
                "szUnit": "pt",
                "color": spec["color"],
                "data-type": "leaf",
            }
        )
        targets.append((attrs["uuid"], block))

    if not targets or len(targets) > 30:
        raise RuntimeError(f"Unexpected heading target count: {len(targets)}")

    for block_id, block in targets:
        output = run_dws(
            "doc",
            "block",
            "update",
            "--node",
            node_id,
            "--block-id",
            block_id,
            "--content-format",
            "jsonml",
            "--element",
            json.dumps(block, ensure_ascii=False, separators=(",", ":")),
        )
        if '"success": true' not in output:
            raise RuntimeError(output)
    return len(targets)


def verify_styles(root):
    counts = {key: 0 for key in STYLES}
    failures = []
    for block in root[2:]:
        key = style_key(block)
        if key is None:
            continue
        counts[key] += 1
        leaf = find_leaf(block) or {}
        spec = STYLES[key]
        if (
            leaf.get("sz") != spec["size"]
            or leaf.get("szUnit") != "pt"
            or leaf.get("color") != spec["color"]
            or leaf.get("bold") is not True
        ):
            failures.append(block[1].get("uuid"))
    if failures or not all(counts.values()):
        raise RuntimeError(f"Native heading verification failed: {failures}, counts={counts}")
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Reapply Codex Document Standard title styles after DingTalk DOCX conversion."
    )
    parser.add_argument("node_id", help="DingTalk online document node ID")
    args = parser.parse_args()

    if shutil.which("dws") is None:
        raise SystemExit("dws CLI is required")

    with tempfile.TemporaryDirectory(prefix="codex-dingtalk-style-") as temp_dir:
        before_path = Path(temp_dir) / "before.json"
        after_path = Path(temp_dir) / "after.json"
        count = apply_styles(args.node_id, read_jsonml(args.node_id, before_path))
        counts = verify_styles(read_jsonml(args.node_id, after_path))

    print(f"PASS updated={count} verified={counts}")


if __name__ == "__main__":
    main()
