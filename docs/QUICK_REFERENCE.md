# Quick Reference: S3 Versioning & Document Generation

## One-Minute Overview

This application generates synthetic enterprise documents with realistic daily churn and automatically uploads them to AWS S3 with **complete version history tracking**.

## Key Features at a Glance

| Feature | Details |
|---------|---------|
| **Document Types** | 16 types (logs, regulatory, audit, claims, KYC/AML, etc.) |
| **Churn Simulation** | Daily updates/deletions with version tracking |
| **S3 Versioning** | Automatic bucket versioning, all versions preserved |
| **Version History** | Complete audit trail with timestamps |
| **Version Tagging** | Named tags for important versions (approved, draft, etc.) |
| **Manifests** | Day snapshots showing current live documents |

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd Day_Document_Generation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export DOCS_S3_BUCKET=documents-churn
```

## Common Commands

### Generate documents locally only
```bash
python app.py --days 5
```

### Generate and upload to S3
```bash
python app.py --days 5 --s3-bucket my-bucket
```

### Generate with custom parameters
```bash
python app.py --days 10 \
  --min-new-docs 3 \
  --max-new-docs 8 \
  --seed 42 \
  --s3-bucket documents-prod
```

### Reconcile and create current snapshot
```bash
python reconcile.py corpus
```

## Document Lifecycle Example

### Day 1
- LOG-123 uploaded (v1)
- REG-456 uploaded (v1)
- API-789 uploaded (v1)

### Day 2
- LOG-123 updated (v2)
- REG-456 retired (no longer in manifest)
- API-789 updated (v2)
- AUD-999 created (v1)

### Day 3
- LOG-123 updated (v3)
- API-789 updated (v3)
- AUD-999 updated (v2)

**Result**: All versions preserved in S3, manifest shows only current live documents

## S3 Storage Layout

```
s3://documents-churn/
├── docs/day1/LOG-123.txt
├── docs/day2/LOG-123.txt (updated version)
├── docs/day3/LOG-123.txt (updated again)
├── manifests/day1/manifest.txt
├── manifests/day2/manifest.txt
└── version-tags/LOG-123/approved.json
```

## Python API Snippets

### Upload a document
```python
from s3_storage import S3DocumentStorage

storage = S3DocumentStorage("my-bucket")
result = storage.upload_document("DOC-001", "content", day=1)
print(result['version_id'])  # e.g., "abc123xyz"
```

### Get version history
```python
versions = storage.get_document_versions("DOC-001")
for v in versions:
    print(f"{v['version_id']}: {v['last_modified']}")
```

### Retrieve specific version
```python
doc = storage.get_document_version("DOC-001", version_id="abc123xyz")
print(doc['content'])
```

### Tag a version
```python
storage.create_version_tag("DOC-001", "approved")
```

### Generate version report
```python
report = storage.generate_version_report("DOC-001")
print(f"Total versions: {report['total_versions']}")
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_ACCESS_KEY_ID` | AWS authentication | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | S3 region | `us-east-1` |
| `DOCS_S3_BUCKET` | Target S3 bucket | `documents-churn` |

## Command-line Arguments

| Argument | Purpose | Default |
|----------|---------|---------|
| `--days` | Number of daily snapshots | 5 |
| `--base-dir` | Local output directory | corpus |
| `--seed` | Random seed (for reproducibility) | None |
| `--min-new-docs` | Min new docs per day | 5 |
| `--max-new-docs` | Max new docs per day | 10 |
| `--s3-bucket` | Override env var DOCS_S3_BUCKET | None |
| `--aws-region` | Override env var AWS_REGION | us-east-1 |

## File Structure After Generation

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
│   │   ├── 001_LOG-123.txt (updated)
│   │   ├── 003_API-789.txt
│   │   └── documents.txt
│   └── manifest.txt
└── current/
    ├── documents/
    │   └── ...
    └── manifest.txt
```

## Versioning Best Practices

1. **Use seeds for reproducibility**
   ```bash
   python app.py --days 5 --seed 12345
   ```

2. **Tag important versions**
   ```python
   storage.create_version_tag("CRITICAL-DOC", "approved")
   ```

3. **Monitor S3 costs** - Versioning increases storage
   ```bash
   aws s3api list-object-versions --bucket documents-churn
   ```

4. **Set lifecycle policies** - Archive old versions
   - Move versions >90 days to Glacier
   - Delete versions >1 year

5. **Enable MFA Delete** - Prevent accidental deletion
   ```bash
   aws s3api put-bucket-versioning --bucket documents-churn \
     --versioning-configuration Status=Enabled,MFADelete=Enabled
   ```

## Troubleshooting

### "AWS credentials not found"
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### "boto3 not installed"
```bash
pip install -r requirements.txt
```

### "Cannot access bucket"
- Check bucket name
- Verify IAM permissions (s3:PutObject, s3:GetObject, s3:ListBucketVersions)
- Verify region

### Check S3 bucket contents
```bash
# List all documents
aws s3 ls s3://documents-churn/docs/ --recursive

# List all versions
aws s3api list-object-versions --bucket documents-churn

# Get specific version
aws s3api get-object --bucket documents-churn \
  --key docs/day1/LOG-123.txt \
  --version-id vAbC1234567890 \
  output.txt
```

## AWS IAM Policy

Minimum permissions needed:

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

## Costs Estimation

- **Storage**: ~1KB per document × 5-10 docs/day × 30 days × # versions = minimal
- **Requests**: ~10-20 PUT requests/day, ~$0.005/1000 requests
- **Versioning**: Same storage as keeping multiple local files

## Test the Implementation

```bash
# Run tests with mocked S3
python -m pytest test_s3_versioning.py -v

# Test with real S3 (requires credentials)
export DOCS_S3_BUCKET=test-documents
python app.py --days 1

# Verify in S3
aws s3 ls s3://test-documents/ --recursive
```

## Documentation Files

- **S3_INTEGRATION.md** - Complete guide (11KB)
- **IMPLEMENTATION_SUMMARY.md** - Full details (10KB)
- **test_s3_versioning.py** - Test examples
- **.env.example** - Configuration template

## Key Takeaways

✅ Documents generated daily with realistic churn
✅ Every version automatically stored in S3
✅ Complete audit trail with timestamps
✅ Version tagging for easy reference
✅ Backward compatible - works locally without S3
✅ Production-ready with proper error handling

## Next Steps

1. **Get AWS credentials** - IAM user with S3 permissions
2. **Create S3 bucket** - `documents-churn` or your choice
3. **Export environment variables** - AWS credentials and bucket name
4. **Run generation** - `python app.py --days 5`
5. **Verify in S3** - `aws s3 ls s3://documents-churn/ --recursive`
6. **Query version history** - Use S3DocumentStorage API

---

**Need Help?**
- See `S3_INTEGRATION.md` for detailed documentation
- See `test_s3_versioning.py` for code examples
- Run `python app.py --help` for all options
