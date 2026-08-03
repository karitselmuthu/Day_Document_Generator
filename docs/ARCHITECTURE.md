# Architecture & Data Flow - S3 Versioning System

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Document Generation System                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   Application       │
│   (app.py)          │
│                     │
│ - Parse args        │
│ - Init S3 storage   │
│ - Orchestrate gen   │
└────────────┬────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    Document Generation Pipeline             │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │ churn.py                            │   │
│  │ - daily_churn()                     │   │
│  │ - generate_churn_over_days()        │   │
│  │                                     │   │
│  │ ┌──────────────────────────────┐   │   │
│  │ │ generators.py                │   │   │
│  │ │ - 16 document types          │   │   │
│  │ │ - Realistic content gen      │   │   │
│  │ └──────────────────────────────┘   │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────────┐   ┌──────────────────────┐
│ Local FS    │   │ S3 Storage Backend   │
│             │   │ (s3_storage.py)      │
│ ✓ corpus/   │   │                      │
│   day1/     │   │ ✓ Versioning        │
│   day2/     │   │ ✓ Metadata tracking │
│   day3/     │   │ ✓ Version tagging   │
│   current/  │   │ ✓ History retrieval │
└─────────────┘   └──────────┬───────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   AWS S3 Bucket    │
                    │                    │
                    │ ✓ docs/day1/      │
                    │ ✓ docs/day2/      │
                    │ ✓ docs/day3/      │
                    │ ✓ manifests/      │
                    │ ✓ version-tags/   │
                    │                    │
                    │ Versioning: ON    │
                    │ MFA Delete: OPTIONAL
                    │ Tagging: Enabled   │
                    └────────────────────┘
```

## Detailed Data Flow

### Daily Document Generation & S3 Upload Flow

```
START: python app.py --days 5 --s3-bucket documents-churn
│
├─ Parse CLI Arguments
│  └─ --days=5, --s3-bucket, --aws-region, etc.
│
├─ Initialize S3Storage
│  ├─ Check AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY
│  ├─ Create boto3 client
│  ├─ Enable versioning on bucket
│  └─ S3DocumentStorage instance ready
│
└─ For each day (1..5):
   │
   ├─ CHURN Phase:
   │  ├─ Load previous day's documents (if exists)
   │  ├─ Random deletions (2-4 docs)
   │  ├─ Random updates (2-4 docs)
   │  │  └─ Add "[UPDATED on Day N]" marker
   │  └─ Generate new documents (5-10 docs)
   │
   ├─ LOCAL STORAGE Phase:
   │  ├─ Create corpus/dayN/documents/ directory
   │  ├─ Write individual document files
   │  ├─ Write manifest.txt (index, doc_id, filename)
   │  └─ Combine documents.txt
   │
   ├─ S3 UPLOAD Phase (if s3_storage provided):
   │  ├─ Prepare documents list:
   │  │  └─ [(doc_id_1, content_1), ..., (doc_id_N, content_N)]
   │  │
   │  ├─ Upload documents_batch():
   │  │  ├─ For each (doc_id, content):
   │  │  │  └─ S3 PUT docs/dayN/{doc_id}.txt
   │  │  │     ├─ Version ID auto-generated (v1, v2, v3, ...)
   │  │  │     ├─ Metadata: doc-id, day, uploaded-at
   │  │  │     └─ Tags: doc_id, day, versioned=true
   │  │  │
   │  │  └─ S3 PUT manifests/dayN/manifest.txt
   │  │     └─ Version ID auto-generated
   │  │
   │  └─ Return upload_result:
   │     ├─ total_uploaded
   │     ├─ total_failed
   │     ├─ documents: [{s3_key, version_id, ...}]
   │     └─ manifest: {success, s3_key, version_id}
   │
   └─ Print summary:
      └─ "Day N: M docs generated with churn"

END ✓
```

## Document Version Lifecycle

### Example: Single Document Across 3 Days

```
LOG-123 Timeline
===============

Day 1:
┌─────────────────────────────────────────┐
│ Action: Create                          │
├─────────────────────────────────────────┤
│ Content: "Application startup log"      │
│ Size: 256 bytes                         │
│ Manifest: YES (listed as live)          │
│ S3 Path: docs/day1/LOG-123.txt          │
│ Version ID: v1                          │
│ Timestamp: 2026-08-03T12:00:00Z         │
│ Metadata: {doc_id, day:1, uploaded_at}  │
└─────────────────────────────────────────┘
         │
         └──► S3: LOG-123.txt (v1)


Day 2:
┌─────────────────────────────────────────┐
│ Action: Update                          │
├─────────────────────────────────────────┤
│ Content: "...startup log [UPDATED on    │
│           Day 2]"                       │
│ Size: 280 bytes                         │
│ Manifest: YES (still listed)            │
│ S3 Path: docs/day2/LOG-123.txt          │
│ Version ID: v2                          │
│ Timestamp: 2026-08-03T13:00:00Z         │
│ Metadata: {doc_id, day:2, uploaded_at}  │
└─────────────────────────────────────────┘
         │
         └──► S3: LOG-123.txt (v2)
              (Same key, new version ID)


Day 3:
┌─────────────────────────────────────────┐
│ Action: Update                          │
├─────────────────────────────────────────┤
│ Content: "...startup log [UPDATED on    │
│           Day 3]"                       │
│ Size: 312 bytes                         │
│ Manifest: YES (still listed)            │
│ S3 Path: docs/day3/LOG-123.txt          │
│ Version ID: v3                          │
│ Timestamp: 2026-08-03T14:00:00Z         │
│ Metadata: {doc_id, day:3, uploaded_at}  │
└─────────────────────────────────────────┘
         │
         └──► S3: LOG-123.txt (v3)
              (Same key, new version ID)

RESULT IN S3:
═════════════

s3://documents-churn/docs/*/LOG-123.txt has 3 versions:

Version History (newest first):
  v3: 2026-08-03T14:00:00Z (312 bytes) - Latest
  v2: 2026-08-03T13:00:00Z (280 bytes)
  v1: 2026-08-03T12:00:00Z (256 bytes) - Original
```

## Manifest Evolution

```
Day 1 Manifest
──────────────
index  doc_id     file_name
001    LOG-001    001_LOG-001.txt
002    REG-002    002_REG-002.txt
003    API-003    003_API-003.txt

S3 Upload: manifests/day1/manifest.txt (v1)


Day 2 Manifest (Churn: deleted REG-002, updated LOG-001, new AUD-004)
──────────────────────────────────────────────────────────────────────
index  doc_id     file_name
001    LOG-001    001_LOG-001.txt     [UPDATED]
002    API-003    002_API-003.txt
003    AUD-004    003_AUD-004.txt     [NEW]

NOTE: REG-002 removed from manifest but still in version history

S3 Upload: manifests/day2/manifest.txt (v1)


Day 3 Manifest (Churn: updated LOG-001, updated AUD-004, new CMP-005)
──────────────────────────────────────────────────────────────────────
index  doc_id     file_name
001    LOG-001    001_LOG-001.txt     [UPDATED AGAIN]
002    API-003    002_API-003.txt
003    AUD-004    003_AUD-004.txt     [UPDATED]
004    CMP-005    004_CMP-005.txt     [NEW]

S3 Upload: manifests/day3/manifest.txt (v1)
```

## S3 Storage Structure After 3 Days

```
s3://documents-churn/
│
├── docs/
│   ├── day1/
│   │   ├── LOG-001.txt
│   │   │   ├── Version v1 (256 bytes, 2026-08-03T12:00:00Z)
│   │   │   └── Version v2 (280 bytes, 2026-08-03T13:00:00Z)
│   │   │   └── Version v3 (312 bytes, 2026-08-03T14:00:00Z)
│   │   ├── REG-002.txt
│   │   │   └── Version v1 (192 bytes, 2026-08-03T12:00:00Z) [RETIRED]
│   │   └── API-003.txt
│   │       └── Version v1 (420 bytes, 2026-08-03T12:00:00Z)
│   │
│   ├── day2/
│   │   ├── LOG-001.txt (same key, v2)
│   │   ├── API-003.txt (same key, v1)
│   │   └── AUD-004.txt
│   │       ├── Version v1 (356 bytes, 2026-08-03T13:00:00Z)
│   │       └── Version v2 (368 bytes, 2026-08-03T14:00:00Z)
│   │
│   └── day3/
│       ├── LOG-001.txt (same key, v3)
│       ├── API-003.txt (same key, v1)
│       ├── AUD-004.txt (same key, v2)
│       └── CMP-005.txt
│           └── Version v1 (287 bytes, 2026-08-03T14:00:00Z)
│
├── manifests/
│   ├── day1/
│   │   └── manifest.txt (v1) - Contains: LOG-001, REG-002, API-003
│   ├── day2/
│   │   └── manifest.txt (v1) - Contains: LOG-001, API-003, AUD-004
│   └── day3/
│       └── manifest.txt (v1) - Contains: LOG-001, API-003, AUD-004, CMP-005
│
└── version-tags/
    ├── LOG-001/
    │   ├── draft.json (points to v2)
    │   ├── approved.json (points to v3)
    │   └── production.json (points to v3)
    ├── REG-002/
    │   └── archived.json (points to v1)
    └── ...
```

## Versioning Strategy

```
S3 Object Versioning: ENABLED
┌────────────────────────────────────────────────────┐
│                                                    │
│  Each PUT creates new version automatically       │
│  All versions preserved until explicitly deleted  │
│  Version ID assigned by S3 (e.g., vAbC1234xyz)   │
│  IsLatest flag tracks current version             │
│                                                    │
└────────────────────────────────────────────────────┘

Metadata Preserved Per Version:
┌────────────────────────────────────────────────────┐
│ S3 Object Metadata:                                │
│  - doc-id: Document identifier                   │
│  - day: Day snapshot number                       │
│  - uploaded-at: ISO timestamp                     │
│                                                    │
│ S3 Object Tags:                                    │
│  - doc_id: Document identifier                   │
│  - day: Day snapshot number                       │
│  - versioned: true                                │
│                                                    │
│ S3 Version Metadata:                              │
│  - VersionId: Unique version ID                   │
│  - LastModified: Timestamp                        │
│  - ETag: Content hash                             │
│  - Size: Content size                             │
│  - IsLatest: Boolean flag                         │
│                                                    │
└────────────────────────────────────────────────────┘

Version Tags (Application Layer):
┌────────────────────────────────────────────────────┐
│ Stored as JSON objects in S3:                      │
│                                                    │
│ version-tags/{doc_id}/{tag_name}.json             │
│                                                    │
│ Example: version-tags/LOG-001/approved.json       │
│ {                                                  │
│   "doc_id": "LOG-001",                            │
│   "tag_name": "approved",                         │
│   "version_id": "v3",                             │
│   "s3_key": "docs/day3/LOG-001.txt",             │
│   "created_at": "2026-08-03T14:30:00Z"           │
│ }                                                  │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Class Diagram: S3DocumentStorage

```
S3DocumentStorage
═════════════════════════════════════════════════════

Attributes:
  - bucket_name: str
  - region: str
  - s3_client: boto3.S3Client

Methods:
  ┌─────────────────────────────────────────────┐
  │ Upload Operations                           │
  ├─────────────────────────────────────────────┤
  │ + upload_document(doc_id, content, day)     │
  │   → Returns: {success, s3_key, version_id}  │
  │                                             │
  │ + upload_documents_batch(day, docs, mani)   │
  │   → Returns: {total_uploaded, total_failed} │
  │                                             │
  │ + upload_manifest(day, manifest_content)    │
  │   → Returns: {success, s3_key}              │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │ Retrieval Operations                        │
  ├─────────────────────────────────────────────┤
  │ + get_document_version(doc_id, version_id)  │
  │   → Returns: {content, version_id, metadata}│
  │                                             │
  │ + get_document_versions(doc_id)             │
  │   → Returns: [{version_id, date, size}...]  │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │ Tagging & Reporting                         │
  ├─────────────────────────────────────────────┤
  │ + create_version_tag(doc_id, tag_name)      │
  │   → Returns: {success, tag_key}             │
  │                                             │
  │ + generate_version_report(doc_id)           │
  │   → Returns: {total_versions, all_versions} │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │ Configuration                               │
  ├─────────────────────────────────────────────┤
  │ - _enable_bucket_versioning()               │
  │   Called automatically on init              │
  └─────────────────────────────────────────────┘
```

## Integration Points

```
Application Layer
├─ app.py
│  └─ Initializes S3DocumentStorage
│     (if AWS credentials present)
│
├─ churn.py
│  ├─ daily_churn()
│  │  └─ Calls s3_storage.upload_documents_batch()
│  │
│  └─ generate_churn_over_days()
│     └─ Passes s3_storage to daily_churn()
│
└─ s3_storage.py
   ├─ Class: S3DocumentStorage
   │  └─ Manages all S3 operations
   │
   └─ Factory: get_s3_storage()
      └─ Creates instance from env vars

Data Persistence
├─ Local: corpus/dayN/documents/
│  └─ Parallel to S3 storage
│
├─ S3: s3://bucket/docs/dayN/
│  └─ Versioned copy of all documents
│
└─ S3: s3://bucket/version-tags/
   └─ Named version pointers
```

## Error Handling & Logging

```
Flow with Error Handling
════════════════════════

upload_document()
  │
  ├─ Try: S3 PUT object
  │  ├─ Success: Return {success:true, version_id}
  │  └─ ClientError: Catch & log
  │     └─ Return {success:false, error}
  │
  └─ Always: Log operation
     ├─ INFO: "Uploaded {doc_id} to {s3_key} (v{version_id})"
     └─ ERROR: "Failed to upload {doc_id}: {error}"

generate_churn_over_days()
  │
  └─ For each day:
     └─ Call daily_churn()
        ├─ Local storage always succeeds
        └─ S3 upload (if provided):
           ├─ Check upload_result['total_failed']
           ├─ If > 0:
           │  └─ Log WARNING: "N documents failed to upload"
           └─ Continue to next day (resilient)
```

## Performance Profile

```
Operation Timing
════════════════

Single Document Upload:
├─ Serialize content: <1ms
├─ Create metadata: <1ms
├─ S3 PUT request: 100-500ms
│  └─ Varies by: size, network, S3 latency
└─ Total: ~100-500ms per document

Batch Upload (10 documents):
├─ Loop through documents: <10ms
├─ Individual uploads: 10 × 100-500ms (parallel capable)
└─ Total: ~1-5 seconds

Version Retrieval:
├─ S3 LIST VERSIONS: 100-300ms
├─ Filter/parse: <10ms
└─ Total: ~100-300ms per document

Memory Usage:
├─ S3 client initialization: ~5MB
├─ Document content: Size of content (streamed)
├─ Version history: Minimal (metadata only)
└─ Total: Generally <100MB for typical workflows
```

---

**Key Insight**: Documents maintain complete version history in S3 while manifests show only current state, enabling both audit trails and current-state reconciliation.
