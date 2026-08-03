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
    start_date: datetime.datetime | None = None,
) -> int:
    if day < 1:
        raise ValueError("day must be >= 1")
    if min_new_docs < 0 or max_new_docs < 0:
        raise ValueError("min_new_docs and max_new_docs must be >= 0")
    if min_new_docs > max_new_docs:
        raise ValueError("min_new_docs must be <= max_new_docs")

    if start_date is None:
        start_date = datetime.datetime.now()
    
    # Calculate date for this day (add days to start_date)
    current_date = start_date + datetime.timedelta(days=day - 1)
    date_folder = current_date.strftime("%d_%m_%y")
    prev_date = start_date + datetime.timedelta(days=day - 2)
    prev_date_folder = prev_date.strftime("%d_%m_%y")
    
    prev_day = os.path.join(base_dir, prev_date_folder)
    day_path = os.path.join(base_dir, date_folder)
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

        upload_result = s3_storage.upload_documents_batch(date_folder, documents_with_ids, manifest_content)
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
    start_date: datetime.datetime | None = None,
) -> list[int]:
    if days < 1:
        raise ValueError("days must be >= 1")

    if start_date is None:
        start_date = datetime.datetime.now()
    
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
            start_date=start_date,
        )
        counts.append(count)
    return counts


def generate_rag_ecosystem(
    output_dir: str = "rag_ecosystem",
    formats: list[str] | None = None,
    s3_storage=None,
) -> dict[str, dict[str, str]]:
    """Generate RAG ecosystem documents with dual format support.
    
    Generates 5 interconnected RAG documents (FEE-407, SOP-843, CIR-574, REG-768, MASTER_GUIDE)
    in both TXT and PDF formats, with 235+ cross-references between documents.
    
    Args:
        output_dir: Output directory for generated documents (default: "rag_ecosystem")
        formats: List of formats to generate (default: ["txt", "pdf"])
        s3_storage: Optional S3 storage backend for uploading documents
        
    Returns:
        Dictionary mapping document IDs to their file paths
        
    Example:
        results = generate_rag_ecosystem(formats=["txt", "pdf"])
        # Returns: {"FEE-407": {"txt": "path/to/FEE-407.txt", "pdf": "path/to/FEE-407.pdf"}, ...}
    """
    try:
        from rag_ecosystem_generator import RAGEcosystemGenerator
    except ImportError:
        raise ImportError("rag_ecosystem_generator module not found. Please ensure it's installed.")
    
    if formats is None:
        formats = ["txt", "pdf"]
    
    print(f"\n{'='*70}")
    print("RAG ECOSYSTEM DOCUMENT GENERATION")
    print(f"{'='*70}")
    print(f"Generating documents in formats: {', '.join(formats).upper()}")
    print(f"Output directory: {output_dir}/\n")
    
    # Initialize and run generator
    generator = RAGEcosystemGenerator(output_dir=output_dir, formats=formats)
    results = generator.generate_all_documents()
    
    # Upload to S3 if storage backend provided
    if s3_storage is not None:
        print(f"\nUploading to S3 bucket: {s3_storage.bucket_name}")
        _upload_rag_ecosystem_to_s3(results, s3_storage)
    
    # Print summary
    print(f"\n{'='*70}")
    print("GENERATION COMPLETE")
    print(f"{'='*70}")
    for doc_id, paths in results.items():
        print(f"\n{doc_id}:")
        for format_type, path in paths.items():
            file_size = _get_file_size(path)
            print(f"  ✓ {format_type.upper()}: {path} ({file_size})")
    
    print(f"\n{'='*70}")
    print(f"Total documents: {len(results)}")
    print(f"Total formats: {len(formats)}")
    print(f"Total cross-references: 235+")
    print(f"{'='*70}\n")
    
    return results


def _upload_rag_ecosystem_to_s3(results: dict[str, dict[str, str]], s3_storage) -> None:
    """Upload generated RAG ecosystem documents to S3.
    
    Args:
        results: Dictionary of generated documents and their paths
        s3_storage: S3 storage backend instance
    """
    for doc_id, paths in results.items():
        for format_type, filepath in paths.items():
            if os.path.exists(filepath):
                # Read file content
                mode = "rb" if format_type == "pdf" else "r"
                encoding = None if format_type == "pdf" else "utf-8"
                
                with open(filepath, mode, encoding=encoding) as f:
                    content = f.read()
                
                # Upload to S3 with RAG ecosystem metadata
                try:
                    s3_storage.upload_document(
                        doc_id=doc_id,
                        content=content,
                        day=None,  # RAG ecosystem docs are not associated with a specific day
                        doc_type="rag-ecosystem",
                        format_type=format_type,
                        metadata={
                            "document_id": doc_id,
                            "generated_at": datetime.datetime.now().isoformat(),
                        }
                    )
                    print(f"  ✓ Uploaded {doc_id} ({format_type.upper()}) to S3")
                except Exception as e:
                    print(f"  ✗ Failed to upload {doc_id} ({format_type.upper()}): {e}")


def _get_file_size(filepath: str) -> str:
    """Get human-readable file size.
    
    Args:
        filepath: Path to file
        
    Returns:
        Human-readable file size string
    """
    if not os.path.exists(filepath):
        return "0 B"
    
    size_bytes = os.path.getsize(filepath)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
