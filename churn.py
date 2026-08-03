import datetime
import os
import random
from typing import Callable, Optional

from generators import generate_documents

DOC_SEPARATOR = "\n---\n"


def _extract_document_id(document: str, fallback_index: int) -> str:
    for line in document.splitlines():
        if line.startswith("Document ID: "):
            return line.replace("Document ID: ", "").strip()
        if '"document_id"' in line:
            _, _, value = line.partition(":")
            doc_id = value.strip().strip('",')
            if doc_id:
                return doc_id
    return f"DOC-{fallback_index:03d}"


def _sanitize_filename(name: str) -> str:
    cleaned = []
    for char in name:
        if char.isalnum() or char in ("-", "_"):
            cleaned.append(char)
        else:
            cleaned.append("_")
    return "".join(cleaned)


def _write_document_files(day_path: str, docs: list[str]) -> None:
    documents_dir = os.path.join(day_path, "documents")
    os.makedirs(documents_dir, exist_ok=True)
    for existing_name in os.listdir(documents_dir):
        existing_path = os.path.join(documents_dir, existing_name)
        if os.path.isfile(existing_path):
            os.remove(existing_path)

    manifest_path = os.path.join(day_path, "manifest.txt")
    manifest_lines: list[str] = []
    for index, document in enumerate(docs, start=1):
        doc_id = _sanitize_filename(_extract_document_id(document, index))
        file_name = f"{index:03d}_{doc_id}.txt"
        file_path = os.path.join(documents_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(document)
        manifest_lines.append(f"{index:03d}\t{doc_id}\t{file_name}")

    with open(manifest_path, "w", encoding="utf-8") as file:
        file.write("index\tdocument_id\tfile_name\n")
        file.write("\n".join(manifest_lines))

    combined_documents_path = os.path.join(documents_dir, "documents.txt")
    with open(combined_documents_path, "w", encoding="utf-8") as file:
        file.write(DOC_SEPARATOR.join(docs))


def daily_churn(
    day: int,
    base_dir: str,
    rng: random.Random,
    now_fn: Callable[[], datetime.datetime],
    min_new_docs: int = 5,
    max_new_docs: int = 10,
    s3_storage=None,
) -> int:
    if day < 1:
        raise ValueError("day must be >= 1")
    if min_new_docs < 0 or max_new_docs < 0:
        raise ValueError("min_new_docs and max_new_docs must be >= 0")
    if min_new_docs > max_new_docs:
        raise ValueError("min_new_docs must be <= max_new_docs")

    prev_day = os.path.join(base_dir, f"day{day-1}")
    day_path = os.path.join(base_dir, f"day{day}")
    os.makedirs(day_path, exist_ok=True)

    docs: list[str] = []
    prev_documents_file = os.path.join(prev_day, "documents", "documents.txt")
    if day > 1 and not os.path.exists(prev_documents_file):
        prev_documents_file = os.path.join(prev_day, "documents.txt")
    if day > 1 and os.path.exists(prev_documents_file):
        with open(prev_documents_file, "r", encoding="utf-8") as file:
            docs = file.read().split(DOC_SEPARATOR)

        for _ in range(rng.randint(2, 4)):
            if docs:
                docs.pop(rng.randint(0, len(docs) - 1))

        for _ in range(rng.randint(2, 4)):
            if docs:
                index = rng.randint(0, len(docs) - 1)
                docs[index] = f"{docs[index]}\n[UPDATED on Day {day}]"

    docs.extend(generate_documents(rng.randint(min_new_docs, max_new_docs), rng, now_fn))

    _write_document_files(day_path, docs)

    # Upload to S3 if storage backend is provided
    if s3_storage is not None:
        documents_with_ids = []
        for index, document in enumerate(docs, start=1):
            doc_id = _sanitize_filename(_extract_document_id(document, index))
            documents_with_ids.append((doc_id, document))

        manifest_path = os.path.join(day_path, "manifest.txt")
        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest_content = file.read()

        upload_result = s3_storage.upload_documents_batch(day, documents_with_ids, manifest_content)
        if upload_result["total_failed"] > 0:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Day {day}: {upload_result['total_failed']} documents failed to upload to S3"
            )

    return len(docs)


def generate_churn_over_days(
    days: int,
    base_dir: str = "corpus",
    seed: int | None = None,
    min_new_docs: int = 5,
    max_new_docs: int = 10,
    s3_storage=None,
) -> list[int]:
    if days < 1:
        raise ValueError("days must be >= 1")

    rng = random.Random(seed)
    counts: list[int] = []
    for day in range(1, days + 1):
        count = daily_churn(
            day=day,
            base_dir=base_dir,
            rng=rng,
            now_fn=datetime.datetime.now,
            min_new_docs=min_new_docs,
            max_new_docs=max_new_docs,
            s3_storage=s3_storage,
        )
        counts.append(count)
    return counts
