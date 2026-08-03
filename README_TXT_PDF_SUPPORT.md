# Mixed Format Support: TXT and PDF Document Generation

## Overview

The Day Document Generation application now supports generating documents in **both TXT and PDF formats**. This provides flexibility for different use cases:

- **TXT Format**: Lightweight, optimized for RAG (Retrieval-Augmented Generation) ingestion, semantic chunking, and embedding
- **PDF Format**: Professional presentation, human-readable documents, suitable for distribution and printing

## Features

### Dual Format Generation
- Generate documents in TXT, PDF, or both formats simultaneously
- Automatic format detection and MIME type handling
- Separate S3 storage paths for each format: `/txt/` and `/pdf/`

### Document Types

#### 1. Standard Daily Churn (Traditional)
- Generates random documents with daily changes
- Simulates document lifecycle: creation, updates, deletions
- Suitable for testing RAG systems with evolving document corpus

#### 2. RAG Ecosystem (New)
- 5 interconnected operational documents with 235+ cross-references
- Documents: FEE-407, SOP-843, CIR-574, REG-768, MASTER_INTERLINKING_GUIDE
- Available in both TXT and PDF formats
- Purpose-built for RAG systems with section-level chunking

### S3 Storage with Versioning
- Dual format support in S3 bucket
- Automatic versioning for all uploaded documents
- Format-aware metadata tagging
- Separate paths for RAG ecosystem vs. standard churn documents

## Usage

### Command 1: Standard Daily Document Churn

Generate 5 days of daily document changes with random variations:

```bash
# Default: TXT only (legacy mode)
python3 app.py churn --days 5

# With S3 upload
python3 app.py churn --days 5 \
  --s3-bucket amzn-rag-doc-generator \
  --aws-region us-east-1
```

Output structure:
```
corpus/
├── day1/
│   ├── documents/
│   │   ├── 001_DOC-001.txt
│   │   ├── 002_DOC-002.txt
│   │   ├── manifest.txt
│   │   └── documents.txt
│   └── manifest.txt
├── day2/
└── day3/
```

### Command 2: RAG Ecosystem Document Generation (New)

Generate 5 interconnected RAG documents with full cross-reference mapping in dual formats:

```bash
# Generate both TXT and PDF
python3 app.py rag-ecosystem \
  --output-dir rag_ecosystem \
  --formats txt pdf

# Generate TXT only
python3 app.py rag-ecosystem --formats txt

# Generate PDF only
python3 app.py rag-ecosystem --formats pdf

# With S3 upload
python3 app.py rag-ecosystem \
  --output-dir rag_ecosystem \
  --formats txt pdf \
  --s3-bucket amzn-rag-doc-generator \
  --aws-region us-east-1
```

Output structure:
```
rag_ecosystem/
├── txt/
│   ├── FEE-407_expanded.txt
│   ├── SOP-843_expanded.txt
│   ├── CIR-574_expanded.txt
│   ├── REG-768_expanded.txt
│   ├── MASTER_INTERLINKING_GUIDE_expanded.txt
│   └── metadata.json
├── pdf/
│   ├── FEE-407_expanded.pdf
│   ├── SOP-843_expanded.pdf
│   ├── CIR-574_expanded.pdf
│   ├── REG-768_expanded.pdf
│   └── MASTER_INTERLINKING_GUIDE_expanded.pdf
└── metadata.json
```

## Document Details

### RAG Ecosystem Documents

#### FEE-407: Fee Structure & Billing Policy
- **Type**: Policy/Reference Document
- **Sections**: 10 main sections + 3 appendices
- **Size**: 4.1 KB (TXT), 7.5 KB (PDF)
- **Purpose**: Defines fee structures, billing cycles, discounts, waivers, and compliance requirements
- **Key Topics**: 
  - Fee structure hierarchy
  - Billing procedures and cycles
  - Discount and waiver protocols
  - Cost allocation rules
  - Compliance checkpoints

#### SOP-843: Standard Operating Procedure
- **Type**: Procedure/Workflow Document
- **Sections**: 13 main sections + 4 appendices
- **Size**: 4.9 KB (TXT), 7.7 KB (PDF)
- **Purpose**: Step-by-step procedures for implementing policies and managing billing operations
- **Key Topics**:
  - Monthly billing cycle (pre-billing, invoice generation, post-invoice)
  - Payment processing workflow
  - Delinquency management (5-stage escalation path)
  - Hardship and payment plans
  - Quarterly reconciliation
  - Dispute resolution process

#### CIR-574: Circular/Notification
- **Type**: Communication/Templates Document
- **Sections**: 12 main sections + 4 appendices
- **Size**: 4.4 KB (TXT), 7.6 KB (PDF)
- **Purpose**: Standardized communication protocols with templates for customer notifications
- **Key Topics**:
  - Fee change notification protocol (T-30 through T+30 days)
  - Service update notifications
  - Policy change communications
  - Payment and delinquency notices (5 stages)
  - Dispute responses and appeals
  - FAQ templates

#### REG-768: Regulatory Documentation
- **Type**: Compliance/Framework Document
- **Sections**: 9 main sections + 4 appendices
- **Size**: 3.7 KB (TXT), 6.7 KB (PDF)
- **Purpose**: Regulatory compliance baseline for all operations
- **Key Topics**:
  - Compliance matrix for fee structures
  - Billing accuracy and procedure compliance
  - Communication compliance
  - Account management compliance
  - Dispute resolution compliance
  - Internal compliance monitoring
  - External audit procedures

#### MASTER_INTERLINKING_GUIDE: Navigation Guide
- **Type**: Master Reference Document
- **Sections**: 15-20 pages of cross-references and navigation maps
- **Size**: 1.9 KB (TXT), 4.7 KB (PDF)
- **Purpose**: Shows relationships and navigation paths between all 4 documents
- **Key Content**:
  - Document relationship matrix
  - Section-by-section interlinking
  - Cross-document query patterns
  - Decision trees for document selection
  - Common workflow scenarios

### Cross-References

All documents include **235+ cross-references** linking related content:

- **Internal links**: Within-document section references
- **External links**: Between-document section references (e.g., "See FEE-407:Section 2")
- **Topic clustering**: Documents organized by operational workflows
- **Query patterns**: Documented workflows showing which documents to consult

### RAG Implementation

The documents are optimized for RAG systems:

1. **Section-level chunking**: Each section is a discrete chunk for embedding
2. **Rich metadata**: Document headers include type, version, generation timestamp
3. **Dense contextual information**: Detailed sections support semantic queries
4. **Cross-reference tracking**: Metadata.json maps all relationships
5. **Appendices**: Structured reference material for lookup queries

## S3 Storage

### Bucket Structure

```
s3://amzn-rag-doc-generator/
├── rag-ecosystem/
│   ├── txt/
│   │   ├── FEE-407_expanded.txt
│   │   ├── SOP-843_expanded.txt
│   │   ├── CIR-574_expanded.txt
│   │   ├── REG-768_expanded.txt
│   │   └── MASTER_INTERLINKING_GUIDE_expanded.txt
│   └── pdf/
│       ├── FEE-407_expanded.pdf
│       ├── SOP-843_expanded.pdf
│       ├── CIR-574_expanded.pdf
│       ├── REG-768_expanded.pdf
│       └── MASTER_INTERLINKING_GUIDE_expanded.pdf
└── docs/
    ├── day1/
    │   ├── 001_DOC-001.txt
    │   ├── 002_DOC-002.txt
    │   └── manifest.txt
    └── day2/
        └── ...
```

### Versioning

- All documents stored with S3 object versioning enabled
- Each upload creates a new version
- Version IDs tracked in metadata
- Tags include document type, format, and generation timestamp

### Metadata Tags

Each S3 object includes tags for filtering and organization:

```json
{
  "doc_id": "FEE-407",
  "doc_type": "rag-ecosystem",
  "format": "txt",
  "versioned": "true"
}
```

## Configuration

### Environment Variables

```bash
# AWS Credentials (required for S3 upload)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# S3 Bucket (optional if using --s3-bucket flag)
export DOCS_S3_BUCKET="amzn-rag-doc-generator"
```

### Setup Instructions

1. **Install dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure AWS credentials**:
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

3. **Verify S3 access**:
```bash
python3 -c "from s3_storage import S3DocumentStorage; print('S3 ready')"
```

## File Format Specifications

### TXT Format

- **Encoding**: UTF-8
- **Line endings**: POSIX (\n)
- **Content type**: text/plain
- **Structure**: Markdown with sections, tables, and cross-references
- **Chunk strategy**: Split by section headers (## Section Title)
- **Best for**: RAG systems, semantic search, embedding models

### PDF Format

- **Encoding**: Binary PDF
- **Content type**: application/pdf
- **Structure**: Multi-page with title page, TOC, and sections
- **Chunk strategy**: PDF pages or section ranges
- **Best for**: Distribution, archival, human review, compliance records

## Testing

### Test RAG Ecosystem Generation

```bash
# Generate test RAG ecosystem in memory
python3 -c "
from churn import generate_rag_ecosystem
results = generate_rag_ecosystem('test_rag', ['txt', 'pdf'])
print('Generated:', len(results), 'documents')
for doc_id, paths in results.items():
    print(f'  {doc_id}: {list(paths.keys())}')
"
```

### Test Format Detection

```bash
# Verify both formats are generated
ls -lah test_rag_ecosystem/txt/
ls -lah test_rag_ecosystem/pdf/
```

### Test S3 Upload

```bash
# Generate and upload to S3
python3 app.py rag-ecosystem \
  --output-dir rag_ecosystem_prod \
  --formats txt pdf \
  --s3-bucket amzn-rag-doc-generator
```

## Integration Examples

### Python Integration

```python
from churn import generate_rag_ecosystem
from s3_storage import S3DocumentStorage

# Generate RAG ecosystem in both formats
results = generate_rag_ecosystem(
    output_dir="rag_ecosystem",
    formats=["txt", "pdf"]
)

# Upload to S3
s3_storage = S3DocumentStorage(bucket_name="amzn-rag-doc-generator")
for doc_id, paths in results.items():
    for format_type, filepath in paths.items():
        with open(filepath, "rb" if format_type == "pdf" else "r") as f:
            content = f.read()
        s3_storage.upload_document(
            doc_id=doc_id,
            content=content,
            doc_type="rag-ecosystem",
            format_type=format_type
        )
```

### RAG Ingestion

```python
# Load documents for RAG system
import json

# Read metadata
with open("rag_ecosystem/metadata.json") as f:
    metadata = json.load(f)

# For each document
for doc_id, doc_info in metadata.get("documents", {}).items():
    # TXT: Load and chunk by sections
    with open(doc_info["txt_path"]) as f:
        txt_content = f.read()
    
    # PDF: Load for archival/compliance
    with open(doc_info["pdf_path"], "rb") as f:
        pdf_content = f.read()
    
    # Index both formats in your RAG system
```

## Troubleshooting

### Issue: `ModuleNotFoundError: reportlab`

**Solution**: Install reportlab dependency
```bash
pip install reportlab
```

### Issue: S3 Upload fails with "Access Denied"

**Solution**: Check AWS credentials and bucket permissions
```bash
# Verify credentials
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# Check bucket access
aws s3 ls s3://amzn-rag-doc-generator/
```

### Issue: PDF files are empty or corrupted

**Solution**: Verify reportlab installation and file permissions
```bash
python3 -c "from reportlab.lib.pagesizes import letter; print('OK')"
```

### Issue: Metadata.json not created

**Solution**: Ensure all documents are generated before running metadata creation
```bash
# Check if generation completed
ls -la rag_ecosystem/txt/
ls -la rag_ecosystem/pdf/
```

## Performance Considerations

### Memory Usage

- **TXT format**: Minimal (typically 2-5 KB per document)
- **PDF format**: Higher (typically 4-8 KB per document due to formatting)
- **Total**: ~40-60 KB for complete 5-document RAG ecosystem

### Generation Time

- **TXT only**: <1 second
- **PDF only**: 2-3 seconds (reportlab rendering)
- **Both formats**: 3-4 seconds total

### S3 Upload Time

- **Per document**: 100-500 ms (depending on network)
- **5 documents (both formats)**: 1-5 seconds

## Best Practices

### For RAG Systems

1. Use **TXT format** for ingestion and embedding
2. Split by section headers for RAG chunking
3. Include cross-reference metadata in chunks
4. Store PDF format separately for compliance/audit

### For Production

1. Enable S3 versioning for all document types
2. Use metadata tags for filtering and organization
3. Monitor S3 upload metrics for performance
4. Implement automated backups for critical documents

### For Development

1. Generate to local filesystem first
2. Test format-specific rendering
3. Validate cross-references before S3 upload
4. Use test bucket for validation

## Future Enhancements

- [ ] DOCX format support
- [ ] HTML format generation
- [ ] Automatic cross-reference validation
- [ ] Document diff tracking across versions
- [ ] Automated RAG chunk generation
- [ ] Multi-language support
- [ ] Template customization for PDF rendering

## Support & Documentation

- **README_RAG_DOCUMENTS.txt**: Detailed RAG ecosystem document guide
- **IMPLEMENTATION.md**: Technical implementation details
- **requirements.txt**: Python dependencies

## Version History

- **v2.0.0** (Current): Added mixed TXT/PDF format support, RAG ecosystem documents
- **v1.0.0**: Initial release with TXT-only support, standard churn generation

---

**Ready to generate documents in both TXT and PDF formats!** 🚀
