"""Merge day1..dayN snapshots in rag_corpus_enterprise into one current state.

Each day folder is a full snapshot (documents/, manifest.txt). Between days,
documents can be added, updated (content changes, same document_id), or
removed (retired). Walking days in order and keeping the last file seen per
document_id, then dropping ids missing from a later day's manifest, gives the
authoritative current set for chunking.
"""
import os
import re
import shutil


def _day_dirs(base_dir: str) -> list[str]:
    days = []
    for name in os.listdir(base_dir):
        m = re.fullmatch(r"day(\d+)", name)
        if m and os.path.isdir(os.path.join(base_dir, name)):
            days.append((int(m.group(1)), name))
    return [name for _, name in sorted(days)]


def reconcile(base_dir: str) -> dict[str, str]:
    """Return {document_id: absolute_file_path} for the latest live state."""
    current: dict[str, str] = {}
    for day_name in _day_dirs(base_dir):
        day_path = os.path.join(base_dir, day_name)
        manifest_path = os.path.join(day_path, "manifest.txt")
        with open(manifest_path, encoding="utf-8") as f:
            lines = f.read().splitlines()[1:]  # skip header

        today = {}
        for line in lines:
            if not line.strip():
                continue
            _, doc_id, file_name = line.split("\t")
            today[doc_id] = os.path.join(day_path, "documents", file_name)

        # today's manifest is the full live set for that day, so it both
        # updates survivors and drops anything retired since the last day
        current = today

    return current


def write_current(base_dir: str, out_dir_name: str = "current") -> str:
    latest = reconcile(base_dir)
    out_dir = os.path.join(base_dir, out_dir_name)
    docs_dir = os.path.join(out_dir, "documents")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(docs_dir)

    manifest_lines = ["index\tdocument_id\tfile_name"]
    for index, (doc_id, src_path) in enumerate(sorted(latest.items()), start=1):
        file_name = os.path.basename(src_path)
        shutil.copy(src_path, os.path.join(docs_dir, file_name))
        manifest_lines.append(f"{index:03d}\t{doc_id}\t{file_name}")

    with open(os.path.join(out_dir, "manifest.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines))

    return out_dir


if __name__ == "__main__":
    import sys
    import tempfile

    def _write_day(base, day, entries):
        d = os.path.join(base, f"day{day}")
        docs = os.path.join(d, "documents")
        os.makedirs(docs, exist_ok=True)
        lines = ["index\tdocument_id\tfile_name"]
        for i, (doc_id, content) in enumerate(entries, start=1):
            fname = f"{i:03d}_{doc_id}.txt"
            with open(os.path.join(docs, fname), "w") as f:
                f.write(content)
            lines.append(f"{i:03d}\t{doc_id}\t{fname}")
        with open(os.path.join(d, "manifest.txt"), "w") as f:
            f.write("\n".join(lines))

    with tempfile.TemporaryDirectory() as tmp:
        _write_day(tmp, 1, [("A", "a1"), ("B", "b1")])
        _write_day(tmp, 2, [("A", "a2-updated"), ("C", "c1")])  # B retired, A updated, C new
        latest = reconcile(tmp)
        assert set(latest) == {"A", "C"}, latest
        with open(latest["A"]) as f:
            assert f.read() == "a2-updated"

        out = write_current(tmp)
        with open(os.path.join(out, "manifest.txt")) as f:
            manifest_text = f.read()
        assert "A" in manifest_text and "C" in manifest_text

    print("self-check passed")

    if len(sys.argv) > 1:
        base = sys.argv[1]
        out = write_current(base)
        print(f"current snapshot written to {out}")
