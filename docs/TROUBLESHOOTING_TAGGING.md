# Troubleshooting: S3 Object Tagging

**Last Updated**: August 3, 2026  
**Applies to**: S3 Document Generation v2.0+ with Graceful Tagging Degradation

---

## 🔍 Overview

This guide helps diagnose and fix issues related to S3 object tagging in the document generation system.

### Quick Diagnosis

| Error Message | Cause | Solution |
|---|---|---|
| `AccessDenied: s3:PutObjectTagging` | Missing IAM permission | Add `s3:PutObjectTagging` to policy |
| `Could not add tags to docs/...` | Tagging permission denied | This is a warning - uploads still succeed |
| Tags not appearing on objects | Permission denied but upload succeeded | Add permission or accept graceful degradation |

---

## ❌ Common Issues

### Issue 1: "AccessDenied: s3:PutObjectTagging"

**When This Happens**:
- You see warnings during `python app.py` execution
- Warnings appear once per document:
  ```
  Could not add tags to docs/day1/LOG-918.txt: An error occurred 
  (AccessDenied) when calling the PutObjectTagging operation
  ```

**Root Cause**:
Your AWS IAM user doesn't have the `s3:PutObjectTagging` permission.

**Severity**: ⚠️ **Warning Only** - Documents still upload successfully!

#### Solution A: Add Missing Permission (Recommended)

1. **Go to AWS IAM Console**: https://console.aws.amazon.com/iam/
2. **Select your user** (e.g., `rag-document-user`)
3. **Click Permissions** tab
4. **Find policy** `S3DocumentGenerationPolicy`
5. **Edit** and add `"s3:PutObjectTagging"` to the actions list

Before:
```json
"Action": [
  "s3:PutObject",
  "s3:GetObject",
  "s3:ListBucket",
  "s3:ListBucketVersions",
  "s3:GetObjectVersion",
  "s3:PutBucketVersioning"
]
```

After:
```json
"Action": [
  "s3:PutObject",
  "s3:GetObject",
  "s3:ListBucket",
  "s3:ListBucketVersions",
  "s3:GetObjectVersion",
  "s3:PutBucketVersioning",
  "s3:PutObjectTagging"
]
```

6. **Save policy**
7. **Wait 30-60 seconds** for IAM to propagate
8. **Re-run generation** (warnings should be gone)

#### Solution B: Accept Graceful Degradation (Quick Fix)

If you can't modify permissions, that's okay! The application handles this gracefully:

- ✅ All documents upload successfully
- ✅ Versioning works normally
- ✅ Metadata stored correctly
- ⚠️ Tags not applied (but not required)

**No action needed** - just ignore the warnings.

---

### Issue 2: Tagging Failure with Different Error

**When This Happens**:
```
Could not add tags to docs/day1/LOG-918.txt: An error occurred 
(InvalidArgument) when calling the PutObjectTagging operation: ...
```

**Root Causes** (by error type):

#### Error: `InvalidArgument`
**Cause**: Tag value format incorrect  
**Solution**: Check tag format in `s3_storage.py` line 104-108 (should be valid AWS tag format)

#### Error: `InvalidBucketName`
**Cause**: Bucket name in command line doesn't match AWS bucket  
**Solution**: Verify bucket name: `aws s3 ls | grep amzn-rag`

#### Error: `NoSuchBucket`
**Cause**: Bucket doesn't exist or typo in name  
**Solution**: Create bucket or fix name in `--s3-bucket` parameter

#### Error: `ServiceUnavailable`
**Cause**: AWS S3 service temporarily unavailable  
**Solution**: Wait 1-2 minutes and retry

---

### Issue 3: Uploads Succeed but Tags Don't Appear

**When This Happens**:
- No error messages
- Documents visible in S3
- Tags missing on objects

**Root Cause**: 
Tagging attempt failed silently (soft error)

**How to Check**:

```bash
# List objects WITH tags
aws s3api head-object \
  --bucket amzn-rag-doc-generator \
  --key docs/day1/LOG-918.txt

# Look for "TagCount" in output
# If TagCount=0 or "TagCount" missing, tags weren't applied
```

**Solution**:
Same as Issue 1 - add `s3:PutObjectTagging` permission

---

## ✅ How to Verify Tagging is Working

### Method 1: Check for Warnings

Run generation and look for warnings:

```bash
python3 app.py --days 1 --s3-bucket amzn-rag-doc-generator --aws-region us-east-1 2>&1 | grep -i "tags"
```

**Result - Tagging Working** (no output):
```
[No warnings about tagging]
```

**Result - Tagging Failing** (shows warnings):
```
Could not add tags to docs/day1/LOG-918.txt: AccessDenied...
Could not add tags to docs/day1/FAQ-385.txt: AccessDenied...
```

### Method 2: Check S3 Object Directly

```bash
aws s3api head-object \
  --bucket amzn-rag-doc-generator \
  --key docs/day1/AUD-938.txt
```

**If Tagging Works** (output includes):
```json
"TagCount": 3,
"Metadata": {
  "doc-id": "AUD-938",
  "day": "1",
  "uploaded-at": "2026-08-03T19:44:47..."
}
```

**If Tagging Fails** (output excludes TagCount or shows 0):
```json
"Metadata": {
  "doc-id": "AUD-938",
  "day": "1",
  "uploaded-at": "2026-08-03T19:44:47..."
}
```

### Method 3: Python Verification Script

```python
#!/usr/bin/env python3
import boto3
import sys

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'amzn-rag-doc-generator'
key = 'docs/day1/AUD-938.txt'

try:
    response = s3.head_object(Bucket=bucket, Key=key)
    tag_count = response.get('TagCount', 0)
    
    if tag_count > 0:
        print(f"✅ Tagging WORKING - Object has {tag_count} tags")
        
        # List the tags
        tags_response = s3.get_object_tagging(Bucket=bucket, Key=key)
        print("\nTags:")
        for tag in tags_response['TagSet']:
            print(f"  {tag['Key']}: {tag['Value']}")
    else:
        print(f"⚠️ Tagging NOT WORKING - Object has no tags")
        print(f"   (Objects still uploaded successfully)")
        
except Exception as e:
    print(f"❌ Error checking tags: {e}")
    print(f"   Object may not exist in S3")
    sys.exit(1)
```

Run it:
```bash
python3 check_tagging.py
```

---

## 🔧 How Application Handles Tagging

### Version 2.0+ (Current - Graceful Degradation)

The application now handles tagging failure gracefully:

```python
# Step 1: Upload object (GUARANTEED to succeed)
response = self.s3_client.put_object(
    Bucket=self.bucket_name,
    Key=s3_key,
    Body=content.encode("utf-8"),
    ContentType="text/plain",
    Metadata={...}
)

# Step 2: Try to add tags (OPTIONAL - fails silently)
try:
    self.s3_client.put_object_tagging(
        Bucket=self.bucket_name,
        Key=s3_key,
        Tagging={"TagSet": [...]}
    )
except ClientError as tag_error:
    logger.warning(f"Could not add tags: {tag_error}")  # Logged, not fatal
    # Application continues!
```

**Result**:
- ✅ Upload always succeeds
- ⚠️ Tags fail gracefully (warning only)
- 📊 100% success rate on document uploads

### Version 1.0 (Old - Strict Tagging)

```python
# Tags applied during upload
response = self.s3_client.put_object(
    Bucket=self.bucket_name,
    Key=s3_key,
    Body=content.encode("utf-8"),
    Tagging=f"doc_id={doc_id}&day={day}"  # Fails if no permission!
)
# If tagging fails → entire upload fails ❌
```

---

## 🎯 Decision Tree: What Should You Do?

```
Are you seeing tagging warnings?
  │
  ├─ YES
  │  │
  │  ├─ Do you need tags? (for searchability/filtering)
  │  │  │
  │  │  ├─ YES → Add s3:PutObjectTagging permission (see Solution A above)
  │  │  │
  │  │  └─ NO → Ignore warnings. Application works fine without tags.
  │  │
  │  └─ Are documents uploading successfully?
  │     │
  │     ├─ YES → Nothing to do. Documents are in S3.
  │     │
  │     └─ NO → Check upload permissions (s3:PutObject)
  │
  └─ NO
     │
     └─ Tagging is working! All permissions are granted. ✅
```

---

## 📋 Tagging Checklist

Use this to verify everything is configured correctly:

```
Permission Related:
☐ IAM user has s3:PutObject permission
☐ IAM user has s3:PutObjectTagging permission
☐ Policy resources include arn:aws:s3:::amzn-rag-doc-generator/*
☐ Waited 30+ seconds after policy change

S3 Configuration:
☐ Bucket exists and is accessible
☐ Bucket versioning is enabled
☐ Bucket name matches --s3-bucket parameter
☐ Region matches --aws-region parameter

Application Configuration:
☐ AWS credentials set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
☐ Credentials belong to user with permissions above
☐ s3_storage.py is version 2.0+ (graceful tagging)
☐ Running latest code

Verification:
☐ Generation runs without errors
☐ Documents appear in S3 bucket
☐ Each document has metadata (doc-id, day, uploaded-at)
☐ (Optional) Tags appear on objects (if permission granted)
```

---

## 🆘 If Issues Persist

1. **Verify IAM Policy** (most common cause):
   ```bash
   # Check which permissions you have
   aws iam get-user-policy --user-name rag-document-user --policy-name S3DocumentGenerationPolicy
   ```

2. **Check Credentials**:
   ```bash
   export AWS_ACCESS_KEY_ID='your_key'
   export AWS_SECRET_ACCESS_KEY='your_secret'
   aws s3 ls  # Should list your buckets
   ```

3. **Test Tagging Directly**:
   ```bash
   aws s3api put-object-tagging \
     --bucket amzn-rag-doc-generator \
     --key docs/day1/test.txt \
     --tagging 'TagSet=[{Key=test,Value=value}]'
   ```

4. **Contact AWS Support** if error is AWS infrastructure related

---

## 📞 Related Documentation

- [IAM_POLICY_SETUP.md](./IAM_POLICY_SETUP.md) - How to configure IAM permissions
- [S3_OBJECTS_VERIFICATION.md](./S3_OBJECTS_VERIFICATION.md) - How to verify objects in S3
- [S3_INTEGRATION.md](./S3_INTEGRATION.md) - S3 integration API reference

---

*Last updated: August 3, 2026*
