import argparse
import os

from churn import generate_churn_over_days, generate_rag_ecosystem


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic daily document churn generator")
    
    # Subcommands for different generation modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Standard churn generation
    churn_parser = subparsers.add_parser("churn", help="Generate standard daily document churn")
    churn_parser.add_argument("--days", type=int, default=5, help="Number of day snapshots to generate")
    churn_parser.add_argument("--base-dir", default="corpus", help="Output base directory")
    churn_parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    churn_parser.add_argument(
        "--min-new-docs",
        type=int,
        default=5,
        help="Minimum number of new documents added per day",
    )
    churn_parser.add_argument(
        "--max-new-docs",
        type=int,
        default=10,
        help="Maximum number of new documents added per day",
    )
    churn_parser.add_argument(
        "--s3-bucket",
        default=None,
        help="S3 bucket name for document storage (overrides DOCS_S3_BUCKET env var)",
    )
    churn_parser.add_argument(
        "--aws-region",
        default=None,
        help="AWS region for S3 (overrides AWS_REGION env var)",
    )
    
    # RAG ecosystem generation
    rag_parser = subparsers.add_parser("rag-ecosystem", help="Generate RAG ecosystem documents with cross-references")
    rag_parser.add_argument(
        "--output-dir",
        default="rag_ecosystem",
        help="Output directory for RAG ecosystem documents",
    )
    rag_parser.add_argument(
        "--formats",
        nargs="+",
        choices=["txt", "pdf"],
        default=["txt", "pdf"],
        help="Formats to generate (default: both txt and pdf)",
    )
    rag_parser.add_argument(
        "--s3-bucket",
        default=None,
        help="S3 bucket name for document storage (overrides DOCS_S3_BUCKET env var)",
    )
    rag_parser.add_argument(
        "--aws-region",
        default=None,
        help="AWS region for S3 (overrides AWS_REGION env var)",
    )
    
    # Legacy support: when no subcommand is provided, run churn mode
    parser.add_argument("--days", type=int, default=5, help="Number of day snapshots to generate")
    parser.add_argument("--base-dir", default="corpus", help="Output base directory")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    parser.add_argument(
        "--min-new-docs",
        type=int,
        default=5,
        help="Minimum number of new documents added per day",
    )
    parser.add_argument(
        "--max-new-docs",
        type=int,
        default=10,
        help="Maximum number of new documents added per day",
    )
    parser.add_argument(
        "--s3-bucket",
        default=None,
        help="S3 bucket name for document storage (overrides DOCS_S3_BUCKET env var)",
    )
    parser.add_argument(
        "--aws-region",
        default=None,
        help="AWS region for S3 (overrides AWS_REGION env var)",
    )
    
    return parser


def _initialize_s3_storage(s3_bucket: str | None = None, aws_region: str | None = None):
    """Initialize S3 storage if credentials are available."""
    s3_storage = None
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        try:
            from s3_storage import S3DocumentStorage

            s3_bucket = s3_bucket or os.getenv("DOCS_S3_BUCKET")
            if s3_bucket:
                s3_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
                s3_storage = S3DocumentStorage(bucket_name=s3_bucket, region=s3_region)
                print(f"S3 storage enabled: {s3_bucket} ({s3_region})")
            else:
                print("S3 bucket not configured. Set DOCS_S3_BUCKET env var or use --s3-bucket")
        except ImportError:
            print("boto3 not installed. Install with: pip install boto3 botocore")
        except Exception as e:
            print(f"Warning: Could not initialize S3 storage: {e}")
    else:
        print("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to enable S3 storage")
    
    return s3_storage


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    # Determine which command to run
    command = args.command if hasattr(args, 'command') and args.command else "churn"
    
    if command == "rag-ecosystem":
        # Generate RAG ecosystem documents
        s3_storage = _initialize_s3_storage(args.s3_bucket, args.aws_region)
        results = generate_rag_ecosystem(
            output_dir=args.output_dir,
            formats=args.formats,
            s3_storage=s3_storage,
        )
        print("\nGenerated RAG ecosystem documents:")
        for doc_id, paths in results.items():
            print(f"  • {doc_id}: {len(paths)} formats")
        return 0
    else:
        # Default: Generate standard daily document churn
        s3_storage = _initialize_s3_storage(args.s3_bucket, args.aws_region)
        
        counts = generate_churn_over_days(
            days=args.days,
            base_dir=args.base_dir,
            seed=args.seed,
            min_new_docs=args.min_new_docs,
            max_new_docs=args.max_new_docs,
            s3_storage=s3_storage,
        )
        for day, count in enumerate(counts, start=1):
            print(f"Day {day}: {count} docs generated with churn.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
