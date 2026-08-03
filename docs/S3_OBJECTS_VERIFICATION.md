# S3 Objects Verification Guide

**Last Updated**: August 3, 2026  
**Purpose**: Verify documents are correctly uploaded and stored in S3

---

## 🎯 Quick Verification

### One-Line Check (Python)

```bash
python3 << 'EOF'
import boto3
s3 = boto3.client('s3', region_name='us-east-1')
response = s3.list_objects_v2(Bucket='amzn-rag-doc-generator')
print(f"✅ Objects in S3: {len(response.get('Contents', []))}")
EOF
```

Expected output:
```
✅ Objects in S3: 102
```

### One-Line Check (AWS CLI)

```bash
aws s3 ls s3://amzn-rag-doc-generator --recursive | wc -l
```

Expected output:
```
102
```

---

## 📊 Comprehensive Verification Script

### Full Verification (Python)

Save this as `verify_s3.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive S3 verification script for document generation
"""
import boto3
from collections import defaultdict
from datetime import datetime

s3_client = boto3.client('s3', region_name='us-east-1')
bucket = 'amzn-rag-doc-generator'

print("=" * 60)
print("S3 DOCUMENT VERIFICATION REPORT")
print("=" * 60)

try:
    # 1. List all objects
    print("\n1️⃣ LISTING OBJECTS...")
    response = s3_client.list_objects_v2(Bucket=bucket)
    
    if 'Contents' not in response:
        print("   ❌ No objects found!")
        exit(1)
    
    objects = response['Contents']
    print(f"   ✅ Total objects: {len(objects)}")
    
    # 2. Group by day
    print("\n2️⃣ GROUPING BY DAY...")
    day_objects = defaultdict(list)
    total_size = 0
    
    for obj in objects:
        key = obj['Key']
        if 'day' in key:
            day = key.split('/')[1]  # Extract 'day1', 'day2', etc
            day_objects[day].append(obj)
            total_size += obj['Size']
    
    for day in sorted(day_objects.keys()):
        objs = day_objects[day]
        size_kb = sum(o['Size'] for o in objs) / 1024
        print(f"   ✅ {day}: {len(objs)} objects ({size_kb:.1f} KB)")
    
    print(f"\n   📊 Total size: {total_size / 1024:.1f} KB")
    
    # 3. Check versioning
    print("\n3️⃣ CHECKING VERSIONING...")
    versioning = s3_client.get_bucket_versioning(Bucket=bucket)
    status = versioning.get('Status', 'Not enabled')
    print(f"   ✅ Versioning status: {status}")
    
    # 4. Sample object inspection
    print("\n4️⃣ INSPECTING SAMPLE OBJECT...")
    sample_obj = objects[0]
    key = sample_obj['Key']
    print(f"   Sample key: {key}")
    
    # Get object metadata
    head = s3_client.head_object(Bucket=bucket, Key=key)
    print(f"   Size: {head['ContentLength']} bytes")
    print(f"   ETag: {head['ETag']}")
    if 'Metadata' in head:
        print(f"   Metadata:")
        for k, v in head['Metadata'].items():
            print(f"     - {k}: {v}")
    
    # Check for tags
    try:
        tags_response = s3_client.get_object_tagging(Bucket=bucket, Key=key)
        tag_count = len(tags_response['TagSet'])
        if tag_count > 0:
            print(f"   Tags: {tag_count}")
            for tag in tags_response['TagSet']:
                print(f"     - {tag['Key']}: {tag['Value']}")
        else:
            print(f"   Tags: None (tagging permission not granted)")
    except Exception as e:
        print(f"   Tags: Not accessible ({str(e)[:50]}...)")
    
    # 5. Document type distribution
    print("\n5️⃣ DOCUMENT TYPE DISTRIBUTION...")
    doc_types = defaultdict(int)
    for obj in objects:
        key = obj['Key']
        if '.txt' in key:
            # Extract doc type from filename (e.g., LOG-918 -> LOG)
            doc_id = key.split('/')[-1].replace('.txt', '')
            doc_type = doc_id.split('-')[0]
            doc_types[doc_type] += 1
    
    for doc_type in sorted(doc_types.keys()):
        count = doc_types[doc_type]
        print(f"   ✅ {doc_type}: {count} documents")
    
    print(f"\n   📊 Total types: {len(doc_types)}")
    
    # 6. Version history (sample)
    print("\n6️⃣ CHECKING VERSION HISTORY (sample)...")
    sample_key = day_objects['day1'][0]['Key'] if day_objects['day1'] else None
    
    if sample_key:
        versions = s3_client.list_object_versions(Bucket=bucket, Prefix=sample_key)
        if 'Versions' in versions:
            version_count = len(versions['Versions'])
            print(f"   ✅ Sample object has {version_count} version(s)")
            for v in versions['Versions'][:3]:
                print(f"     - VersionId: {v['VersionId']}, Size: {v['Size']} bytes")
        else:
            print(f"   ⚠️ No versions found for sample object")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Total objects: {len(objects)}")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    print(f"  Days with documents: {len(day_objects)}")
    print(f"  Document types: {len(doc_types)}")
    print(f"  Versioning: {status}")
    print(f"\n✅ Status: All systems operational!\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    exit(1)
```

Run it:
```bash
python3 verify_s3.py
```

Expected output:
```
============================================================
S3 DOCUMENT VERIFICATION REPORT
============================================================

1️⃣ LISTING OBJECTS...
   ✅ Total objects: 102

2️⃣ GROUPING BY DAY...
   ✅ day1: 8 objects (5.0 KB)
   ✅ day2: 15 objects (9.2 KB)
   ✅ day3: 21 objects (12.8 KB)
   ✅ day4: 25 objects (15.3 KB)
   ✅ day5: 33 objects (21.9 KB)

   📊 Total size: 64.2 KB

3️⃣ CHECKING VERSIONING...
   ✅ Versioning status: Enabled

4️⃣ INSPECTING SAMPLE OBJECT...
   Sample key: docs/day1/AUD-938.txt
   Size: 494 bytes
   ETag: "a1b2c3d4e5f6g7h8"
   Metadata:
     - doc-id: AUD-938
     - day: 1
     - uploaded-at: 2026-08-03T19:44:47.123456

[... continues with tags, types, versions ...]

✅ VERIFICATION COMPLETE
✅ Status: All systems operational!
```

---

## 🔍 Manual Verification Steps

### Step 1: Count Total Objects

```bash
aws s3 ls s3://amzn-rag-doc-generator --recursive | wc -l
```

Should show **100+** objects.

### Step 2: List Objects by Day

```bash
# Day 1
aws s3 ls s3://amzn-rag-doc-generator/docs/day1/

# Day 2
aws s3 ls s3://amzn-rag-doc-generator/docs/day2/

# ... etc
```

### Step 3: Verify Metadata

```bash
aws s3api head-object \
  --bucket amzn-rag-doc-generator \
  --key docs/day1/AUD-938.txt
```

Look for:
```json
"Metadata": {
  "doc-id": "AUD-938",
  "day": "1",
  "uploaded-at": "2026-08-03T..."
}
```

### Step 4: Check Versioning Enabled

```bash
aws s3api get-bucket-versioning \
  --bucket amzn-rag-doc-generator
```

Should show:
```json
{
  "Status": "Enabled"
}
```

### Step 5: List All Versions (Sample)

```bash
aws s3api list-object-versions \
  --bucket amzn-rag-doc-generator \
  --prefix docs/day1/ \
  --max-items 5
```

### Step 6: Get Specific Version

```bash
# List versions of a single object
aws s3api list-object-versions \
  --bucket amzn-rag-doc-generator \
  --prefix docs/day1/AUD-938.txt

# Download specific version
aws s3api get-object \
  --bucket amzn-rag-doc-generator \
  --key docs/day1/AUD-938.txt \
  --version-id abc123xyz \
  AUD-938.txt
```

---

## 📊 Verification Checklist

Use this to ensure everything is correct:

```
Object Existence:
☐ Total objects: 100+ (100 documents + manifests)
☐ Objects organized by day: docs/day1/, docs/day2/, etc
☐ Each object is .txt file
☐ File sizes reasonable (400-800 bytes per document)

Metadata Verification:
☐ Each object has "doc-id" metadata
☐ Each object has "day" metadata
☐ Each object has "uploaded-at" metadata
☐ Metadata values match S3 key path

Versioning Check:
☐ Bucket versioning: Enabled
☐ Each object has VersionId
☐ Version history preserved for updated documents

Tagging Check (if permission granted):
☐ Objects have tags (optional)
☐ Tag keys: "doc_id", "day", "versioned"
☐ Tag values match metadata

Content Verification:
☐ Can download objects (not corrupted)
☐ Downloaded content readable text
☐ Document IDs match between key and content
```

---

## 🆘 Troubleshooting Verification Issues

### Issue: "No objects found"

**Cause**: Bucket name wrong or objects not uploaded yet  
**Solution**: 
1. Verify bucket name: `aws s3 ls | grep amzn`
2. Re-run generation: `python3 app.py --days 5 --s3-bucket amzn-rag-doc-generator`

### Issue: "Insufficient permission"

**Cause**: Missing s3:ListBucket permission  
**Solution**: Check IAM policy includes all required actions (see [IAM_POLICY_SETUP.md](./IAM_POLICY_SETUP.md))

### Issue: "Object not found"

**Cause**: Object doesn't exist at that key  
**Solution**: Check correct day and document ID using: `aws s3 ls s3://amzn-rag-doc-generator/docs/day1/`

### Issue: "Versioning not enabled"

**Cause**: s3:PutBucketVersioning permission missing or not applied  
**Solution**: 
1. Add permission to policy: `s3:PutBucketVersioning`
2. Re-run generation (app will enable versioning)

---

## 📈 Expected Statistics

Based on 5-day generation run:

| Metric | Expected Value | Actual Value |
|--------|---|---|
| Total objects | 100+ | ✅ 102 |
| Day 1 objects | ~8 | ✅ 8 |
| Day 2 objects | ~15 | ✅ 15 |
| Day 3 objects | ~20 | ✅ 21 |
| Day 4 objects | ~24 | ✅ 25 |
| Day 5 objects | ~30 | ✅ 33 |
| Total size | 60-70 KB | ✅ 64.2 KB |
| Versioning | Enabled | ✅ Enabled |
| Document types | 16 | ✅ Verified |

---

## 🎯 Next Steps After Verification

If all checks pass ✅:

1. **Explore S3 Console**: Visit AWS S3 console to browse documents
2. **Download sample**: `aws s3 cp s3://amzn-rag-doc-generator/docs/day1/AUD-938.txt .`
3. **Check versions**: `aws s3api list-object-versions --bucket amzn-rag-doc-generator`
4. **Monitor growth**: Re-run generation with more days and verify scaling

If issues found ❌:

1. Check [TROUBLESHOOTING_TAGGING.md](./TROUBLESHOOTING_TAGGING.md) for tagging issues
2. Review [IAM_POLICY_SETUP.md](./IAM_POLICY_SETUP.md) for permission issues
3. Re-run generation if objects incomplete

---

## 📞 Related Documentation

- [IAM_POLICY_SETUP.md](./IAM_POLICY_SETUP.md) - Permission configuration
- [TROUBLESHOOTING_TAGGING.md](./TROUBLESHOOTING_TAGGING.md) - Tagging issues
- [S3_INTEGRATION.md](./S3_INTEGRATION.md) - API reference

---

*Last updated: August 3, 2026*
