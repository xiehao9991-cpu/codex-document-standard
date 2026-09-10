"""Restore native heading/table typography with complete recursive coverage."""
import argparse
import copy
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from table_format_common import DEFAULT_FONT, NATIVE_SIZE, cell_alignment, row_style, table_role

STYLES = {
    "Title": {"size": 18, "color": "#2F75B5", "before": "8pt", "after": "4pt"},
    "h1": {"size": 14, "color": "#2F75B5", "before": "8pt", "after": "4pt"},
    "h2": {"size": 12.5, "color": "#2F75B5", "before": "8pt", "after": "4pt"},
    "h3": {"size": 11.5, "color": "#2F75B5", "before": "8pt", "after": "4pt"},
}


def run_dws(*args, input_text=None):
    result = subprocess.run(["dws", *args, "--format", "json"], capture_output=True,
                            text=True, encoding="utf-8", timeout=120, input=input_text)
    if result.returncode != 0:
        # dws may report a write that succeeded but failed its generic verifier.
        # The caller must read and compare the actual block before proceeding.
        for stream in (result.stdout, result.stderr):
            try:
                error = json.loads(stream).get("error", {})
            except ValueError:
                continue
            if error.get("reason") == "doc_write_verification_failed" and error.get("execution_started") is True:
                return stream
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def read_jsonml(node_id, output_path):
    run_dws("doc", "read", "--node", node_id, "--content-format", "jsonml", "--output", str(output_path))
    return json.loads(output_path.read_text(encoding="utf-8"))["jsonml"]


def walk(node, skip_nested_tables=False):
    if not isinstance(node, list) or len(node) < 2 or not isinstance(node[1], dict):
        return
    yield node
    for child in node[2:]:
        if isinstance(child, list) and not (skip_nested_tables and child and child[0] == "table"):
            yield from walk(child, skip_nested_tables)


def leaf_nodes(node, own=False):
    for item in walk(node, skip_nested_tables=own):
        if item[0] == "span" and item[1].get("data-type") == "leaf":
            yield item


def iter_leaves(node):
    for item in leaf_nodes(node):
        yield item[1]


def find_leaf(node):
    return next(iter_leaves(node), None)


def own_text(node):
    return "".join(value for item in leaf_nodes(node, own=True)
                   for value in item[2:] if isinstance(value, str))


def rows_and_cells(table):
    return [[cell for cell in walk(row, True) if cell[0] == "tc" and not cell[1].get("hidden")]
            for row in walk(table, True) if row[0] == "tr"]


def role_of(table):
    rows = rows_and_cells(table)
    columns = max([sum(int(c[1].get("colSpan", 1)) for c in row) for row in rows] or [0])
    columns = max(columns, len(table[1].get("colsWidth", [])))
    nested = any(n is not table and n[0] == "table" for n in walk(table))
    explicit = str(table[1].get("caption", "")).removeprefix("codex:")
    return table_role(len(rows), columns, [c[1].get("fill") for row in rows for c in row], nested, explicit)


def inventory(root):
    return [(n, role_of(n)) for n in walk(root) if n[0] == "table"]


def is_standard_table(block):
    return isinstance(block, list) and len(block) > 1 and block[0] == "table" and role_of(block) == "data"


def style_key(block):
    if not isinstance(block, list) or len(block) < 2 or not isinstance(block[1], dict):
        return None
    if block[0] == "p" and block[1].get("styleId") == "Title":
        return "Title"
    return block[0] if block[0] in {"h1", "h2", "h3"} else None


def paragraph_text(node):
    """Retain explicit native breaks; empty br leaf spans carry no text."""
    if not isinstance(node, list) or len(node) < 2:
        return ""
    if node[0] == "br":
        return "\n"
    if node[0] == "table":
        return ""
    return "".join(child if isinstance(child, str) else paragraph_text(child) for child in node[2:])


def table_targets(table, font=DEFAULT_FONT):
    rows = rows_and_cells(table)
    if not rows:
        return
    width = max(sum(int(c[1].get("colSpan", 1)) for c in rows[0]), len(table[1].get("colsWidth", [])))
    for ri, row in enumerate(rows):
        section = len(row) == 1 and int(row[0][1].get("colSpan", 1)) >= width > 1
        style = row_style(ri, section)
        for cell in row:
            # Native JSONML widths are CSS pixels even when the type label is dxa.
            # The editor's default horizontal padding is approximately 8 px per side.
            width_px = cell[1].get("width", {}).get("w")
            available = max(0, (float(width_px) - 16) * .75) if isinstance(width_px, (float, int)) else None
            paragraphs = [paragraph_text(p) for p in walk(cell, True) if p[0] == "p"]
            yield cell, style, cell_alignment(paragraphs, available, NATIVE_SIZE, font, style["bold"])


def set_fonts(attrs, font):
    attrs["fonts"] = {"ascii": font, "eastAsia": font, "hAnsi": font}


def spacing(before="2pt", after="2pt", line=1.05):
    return {"before": before, "after": after, "line": line, "lineRule": "auto"}


def normalize_root(root, font=DEFAULT_FONT):
    for block in walk(root, True):
        key = style_key(block)
        if key:
            spec = STYLES[key]
            block[1]["spacing"] = spacing(spec["before"], spec["after"], 1.15)
            for leaf in iter_leaves(block):
                set_fonts(leaf, font)
                leaf.update({"sz": spec["size"], "szUnit": "pt", "bold": True, "color": spec["color"]})
        elif block[0] == "p":
            for leaf in iter_leaves(block):
                set_fonts(leaf, font)
    for table, role in inventory(root):
        if role != "data":
            continue
        for cell, style, alignment in table_targets(table, font):
            if style["fill"]:
                cell[1]["fill"] = "#" + style["fill"]
            for p in walk(cell, True):
                if p[0] == "p":
                    p[1]["jc"] = alignment
                    p[1]["spacing"] = spacing()
            for node in leaf_nodes(cell, own=True):
                set_fonts(node[1], font)
                node[1].update({"sz": NATIVE_SIZE, "szUnit": "pt", "bold": style["bold"],
                                "color": "#" + style["color"]})


def verify_styles(root, expected_tables=None, font=DEFAULT_FONT):
    tables = inventory(root)
    failures, headings = [], Counter()
    if expected_tables is not None and len(tables) != expected_tables:
        failures.append(f"table coverage expected={expected_tables}, actual={len(tables)}")
    for block in walk(root, True):
        key = style_key(block)
        if not key:
            continue
        headings[key] += 1
        spec = STYLES[key]
        leaves = list(iter_leaves(block))
        if not leaves or block[1].get("spacing") != spacing(spec["before"], spec["after"], 1.15):
            failures.append(f"heading spacing/content: {block[1].get('uuid')}")
        for attrs in leaves:
            if (attrs.get("sz") != spec["size"] or attrs.get("szUnit") != "pt"
                or attrs.get("bold") is not True or attrs.get("color") != spec["color"]):
                failures.append(f"heading leaf: {block[1].get('uuid')}")
    for table, role in tables:
        if role != "data":
            continue
        key = table[1].get("uuid", "table")
        for cell, spec, align in table_targets(table, font):
            if spec["fill"] and str(cell[1].get("fill", "")).lstrip("#").upper() != spec["fill"]:
                failures.append(f"{key}: fill")
            for p in walk(cell, True):
                if p[0] == "p" and (p[1].get("jc") != align or p[1].get("spacing") != spacing()):
                    failures.append(f"{key}: alignment/spacing")
            for node in leaf_nodes(cell, own=True):
                attrs = node[1]
                if (attrs.get("sz") != NATIVE_SIZE or attrs.get("szUnit") != "pt"
                    or attrs.get("bold") != spec["bold"] or attrs.get("color") != "#" + spec["color"]
                    or any(attrs.get("fonts", {}).get(k) != font for k in ("ascii", "eastAsia", "hAnsi"))):
                    failures.append(f"{key}: text leaf")
    if failures:
        raise RuntimeError("Native verification failed: " + "; ".join(failures[:20]))
    return {"tables": len(tables), "roles": dict(Counter(role for _, role in tables)),
            "headings": dict(headings), "data_size_pt": NATIVE_SIZE, "font": font,
            "soft_wrap_check": "estimated; render review required", "failures": 0}


def apply_styles(node_id, root, font=DEFAULT_FONT):
    before = copy.deepcopy(root)
    count = len(inventory(root))
    normalize_root(root, font)
    verify_styles(root, count, font)
    updates = []
    for old, new in zip(before[2:], root[2:]):
        if old != new:
            if not isinstance(new, list) or not new[1].get("uuid"):
                raise RuntimeError("Changed top-level block has no updateable UUID")
            updates.append(new)
    # Update containing blocks once; nested cells must not be sent as root blocks.
    for block in updates:
        # stdin avoids the Windows command-line length limit on large/nested tables.
        output = run_dws("doc", "+update", "--node", node_id, "--command", "block_replace",
                         "--block-id", block[1]["uuid"], "--doc-format", "jsonml", "--content", "-", "--yes",
                         input_text=json.dumps(block, ensure_ascii=False, separators=(",", ":")))
        result = json.loads(output)
        if result.get("error", {}).get("reason") == "doc_write_verification_failed":
            with tempfile.TemporaryDirectory(prefix="codex-block-check-") as folder:
                current = read_jsonml(node_id, Path(folder) / "actual.json")
            actual = next((n for n in current[2:] if isinstance(n, list)
                           and n[1].get("uuid") == block[1]["uuid"]), None)
            if without_uuids(actual) == without_uuids(block):
                continue
            raise RuntimeError("Native block write was partial or changed content; stopped after read-back comparison")
        if not (result.get("success") is True or (result.get("ok") is True and result.get("complete") is True)):
            raise RuntimeError(output)
    return len(updates)


def without_uuids(value):
    if isinstance(value, list):
        return [without_uuids(v) for v in value]
    if isinstance(value, dict):
        return {k: without_uuids(v) for k, v in value.items() if k != "uuid"}
    return value


def count_empty_paragraphs(root):
    # Word requires terminal paragraphs in table cells; they are not spacer blocks.
    return sum(n[0] == "p" and not own_text(n).strip() for n in walk(root, True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("node_id")
    parser.add_argument("--font", default=DEFAULT_FONT)
    parser.add_argument("--expected-tables", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if shutil.which("dws") is None:
        raise SystemExit("dws CLI is required")
    with tempfile.TemporaryDirectory(prefix="codex-table-style-") as folder:
        root = read_jsonml(args.node_id, Path(folder) / "before.json")
        expected = args.expected_tables if args.expected_tables is not None else len(inventory(root))
        if len(inventory(root)) != expected:
            raise RuntimeError(f"Source/import table count differs: expected={expected}, actual={len(inventory(root))}")
        text_before = [tuple(n[2:]) for n in leaf_nodes(root)]
        if not args.check:
            apply_styles(args.node_id, root, args.font)
            root = read_jsonml(args.node_id, Path(folder) / "after.json")
        report = verify_styles(root, expected, args.font)
        if text_before != [tuple(n[2:]) for n in leaf_nodes(root)]:
            raise RuntimeError("Native text content changed")
        report["empty_paragraphs"] = count_empty_paragraphs(root)
        if report["empty_paragraphs"]:
            raise RuntimeError(f"Unexpected spacer paragraphs: {report['empty_paragraphs']}")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
