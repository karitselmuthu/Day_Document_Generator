# Document Generation with S3 Storage and Versioning

A synthetic daily document churn generator that creates realistic document lifecycle scenarios (new, updated, deleted) across multiple snapshots and stores them in AWS S3 with automatic versioning.

## Features

### Document Generation
- Generates 16 types of enterprise documents (logs, regulatory frameworks, audit reports, KYC/AML guidelines, etc.)
- Simulates daily document churn with configurable document additions
- Tracks document updates and deletions across snapshots
- Maintains manifest files for each snapshot

### S3 Storage & Versioning
- **Automatic Versioning**: S3 object versioning is automatically enabled per bucket
- **Version Tracking**: Every document version is preserved with:
  - Unique version ID
  - Upload timestamp
  - Content metadata (size, ETag)
  - Document tags for tracking

- **Version History**: Access all versions of any document with full metadata
- **Version Tagging**: Create named version tags (e.g., "approved", "draft") for easy reference
- **Manifest Management**: Each day's manifest is also versioned in S3

## Installation

### Local Setup
```bash
# Clone or navigate to the project
cd Day_Document_Generation

# Install dependencies
pip install -r requirements.txt
```

### AWS Configuration
Set up AWS credentials in one of these ways:

#### Option 1: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
export DOCS_S3_BUCKET=documents-churn
```

#### Option 2: AWS CLI Credentials File
```bash
# Configure with AWS CLI
aws configure

# Specify region and bucket via environment
export DOCS_S3_BUCKET=documents-churn
export AWS_REGION=us-east-1
```

#### Option 3: Using .env File
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env

# Source the environment
source .env
```

## Usage

### Generate Documents with Local Storage Only
```bash
# Generate 5 days of documents locally
python app.py --days 5

# Generate 10 days with 3-5 new documents per day
python app.py --days 10 --min-new-docs 3 --max-new-docs 5

# Generate with specific random seed for reproducibility
python app.py --days 7 --seed 42
```

### Generate Documents with S3 Upload
```bash
# Generate documents and upload to S3
python app.py --days 5 --s3-bucket my-docs-bucket

# Specify AWS region
python app.py --days 5 --s3-bucket my-docs-bucket --aws-region us-west-2

# Use environment configuration
export DOCS_S3_BUCKET=documents-churn
export AWS_REGION=us-east-1
python app.py --days 5
```

### Generate and Reconcile
```bash
# Generate documents and create current snapshot
python app.py --days 5 --base-dir corpus
python reconcile.py corpus
```

## S3 Storage Structure

Documents are organized in S3 as follows:

```
s3://documents-churn/
├── docs/
│   ├── day1/
│   │   ├── LOG-123.txt (version 1)
│   │   ├── LOG-123.txt (version 2 - after update)
│   │   ├── REG-456.txt
│   │   └── ...
│   ├── day2/
│   │   ├── LOG-123.txt (version 3)
│   │   ├── API-789.txt (new)
│   │   └── ...
│   └── ...
│
├── manifests/
│   ├── day1/
│   │   └── manifest.txt (version 1)
│   ├── day2/
│   │   └── manifest.txt (version 1)
│   └── ...
│
└── version-tags/
    ├── LOG-123/
    │   ├── approved.json
    │   └── draft.json
    └── ...
```

## Python API Usage

### Basic Upload
```python
from s3_storage import S3DocumentStorage

# Create storage client
storage = S3DocumentStorage(
    bucket_name="my-docs-bucket",
    region="us-east-1",
    enable_versioning=True
)

# Upload a single document
result = storage.upload_document(
    doc_id="LOG-123",
    content="Document content here",
    day=1,
    metadata={"source": "logs", "category": "info"}
)

print(f"Upload successful: {result['success']}")
print(f"Version ID: {result['version_id']}")
print(f"S3 Key: {result['s3_key']}")
```

### Batch Upload
```python
# Upload multiple documents for a day
documents = [
    ("LOG-123", "Log content"),
    ("REG-456", "Regulatory framework"),
    ("AUD-789", "Audit report"),
]

manifest_content = """index\tdocument_id\tfile_name
001\tLOG-123\t001_LOG-123.txt
002\tREG-456\t002_REG-456.txt
003\tAUD-789\t003_AUD-789.txt"""

result = storage.upload_documents_batch(
    day=1,
    documents=documents,
    manifest_content=manifest_content
)

print(f"Uploaded: {result['total_uploaded']}")
print(f"Failed: {result['total_failed']}")
```

### Retrieve Document Versions
```python
# Get all versions of a document
versions = storage.get_document_versions("LOG-123")
for version in versions:
    print(f"Version {version['version_id']}: {version['last_modified']}")

# Get a specific version
doc = storage.get_document_version("LOG-123", version_id="v1234567890")
print(doc['content'])

# Get latest version
doc = storage.get_document_version("LOG-123")
print(doc['content'])
```

### Version Tagging
```python
# Create a named version tag
tag_result = storage.create_version_tag(
    doc_id="LOG-123",
    tag_name="approved"
)

if tag_result['success']:
    print(f"Tag created: {tag_result['tag_key']}")
```

### Version Reports
```python
# Generate comprehensive version report
report = storage.generate_version_report("LOG-123")

print(f"Document: {report['doc_id']}")
print(f"Total versions: {report['total_versions']}")
print(f"Latest version ID: {report['latest_version']['version_id']}")
print(f"First version ID: {report['first_version']['version_id']}")
```

## Document Lifecycle

The application simulates realistic document lifecycle:

1. **Day 1**: Initial documents created and uploaded
2. **Day 2-N**: 
   - Existing documents may be updated (content changes, same document_id)
   - Some documents may be deleted (retired from manifest)
   - New documents are added
   - All versions are preserved in S3
   - Manifest reflects current state (live documents only)

### Example Update Tracking
```
Day 1:
  manifest.txt: LOG-123, REG-456, API-789
  S3 versions: LOG-123 (v1), REG-456 (v1), API-789 (v1)

Day 2:
  manifest.txt: LOG-123, API-789, AUD-999  # REG-456 retired
  S3 versions: LOG-123 (v1, v2), REG-456 (v1), API-789 (v1, v2), AUD-999 (v1)
  Note: REG-456 is no longer in manifest but version history is preserved
```

## Monitoring & Logging

The module uses Python's standard logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# All operations are logged:
# - Document uploads with version IDs
# - Manifest uploads
# - Version retrievals
# - Errors and warnings
```

## Testing

### Local Testing (No AWS Required)
```bash
python -m pytest tests/ -v
```

### Integration Testing (Requires AWS)
```bash
export DOCS_S3_BUCKET=test-documents-churn
export AWS_REGION=us-east-1
python app.py --days 3 --s3-bucket $DOCS_S3_BUCKET
```

## Configuration Reference

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required for S3 |
| `AWS_REGION` | AWS region for S3 | us-east-1 |
| `DOCS_S3_BUCKET` | S3 bucket name | documents-churn |

### Command-line Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--days` | Number of day snapshots | 5 |
| `--base-dir` | Local output directory | corpus |
| `--seed` | Random seed for reproducibility | None |
| `--min-new-docs` | Minimum new docs per day | 5 |
| `--max-new-docs` | Maximum new docs per day | 10 |
| `--s3-bucket` | S3 bucket name | From env var |
| `--aws-region` | AWS region | us-east-1 |

## Troubleshooting

### "AWS credentials not found"
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### "Could not enable versioning"
- S3 bucket may not exist
- IAM user may lack `s3:PutBucketVersioning` permission
- Bucket may already have versioning enabled

### "boto3 not installed"
```bash
pip install -r requirements.txt
```

### S3 Upload Failures
- Check IAM permissions: `s3:PutObject`, `s3:GetObject`, `s3:ListBucketVersions`
- Verify bucket exists and region is correct
- Check AWS credentials validity

## AWS IAM Permissions

Required IAM policy for document storage:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucketVersions",
        "s3:GetObjectVersion",
        "s3:PutBucketVersioning",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::documents-churn",
        "arn:aws:s3:::documents-churn/*"
      ]
    }
  ]
}
```

## Output Examples

### Local Directory Structure
```
corpus/
├── day1/
│   ├── documents/
│   │   ├── 001_LOG-123.txt
│   │   ├── 002_REG-456.txt
│   │   └── documents.txt
│   └── manifest.txt
├── day2/
│   ├── documents/
│   │   ├── 001_LOG-123.txt
│   │   ├── 003_API-789.txt
│   │   └── documents.txt
│   └── manifest.txt
└── current/
    ├── documents/
    │   └── ...
    └── manifest.txt
```

### S3 Upload Log Output
```
Uploaded LOG-123 to s3://documents-churn/docs/day1/LOG-123.txt (vAbC1234567890)
Uploaded REG-456 to s3://documents-churn/docs/day1/REG-456.txt (vXyZ9876543210)
Uploaded manifest for day 1 to manifests/day1/manifest.txt
Day 1: 8 docs generated with churn.
```

## Architecture

### Document Flow
```
generate_documents() → daily_churn() → S3DocumentStorage.upload_documents_batch()
                          ↓
                    _write_document_files()
                    (Local storage)
                          ↓
                    S3 upload
                    (Versioning
                     enabled)
```

### Versioning Strategy
- **Automatic**: S3 object versioning manages all versions
- **Explicit**: Application tracks version IDs in metadata
- **Tagged**: Named version tags for bookmarking important versions
- **Queryable**: Full version history available per document

## Best Practices

1. **Use Seeds**: For reproducible document sets in testing
   ```bash
   python app.py --days 5 --seed 12345
   ```

2. **Monitor Costs**: S3 versioning increases storage costs
   - Set lifecycle policies to archive old versions
   - Regularly clean up retired documents

3. **Backup Important Versions**: Use version tags
   ```python
   storage.create_version_tag("CRITICAL-DOC-001", "approved")
   ```

4. **Audit Trail**: Check S3 versioning logs and CloudTrail
   ```bash
   aws s3api list-object-versions --bucket documents-churn
   ```

5. **Performance**: For large batches, use batch upload
   ```python
   storage.upload_documents_batch(day, documents, manifest)
   ```

## Contributing

Improvements welcome! Consider:
- Additional document types
- More sophisticated churn simulation
- Performance optimizations for large-scale generation
- Integration with data lakes or data warehouses

## License

MIT License - See LICENSE file
