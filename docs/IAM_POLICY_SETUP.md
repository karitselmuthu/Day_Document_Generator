# IAM Policy Setup Guide for S3 Document Generation

**Last Updated**: August 3, 2026  
**Applies to**: AWS S3 Document Generation with Versioning & Tagging

---

## 📋 Overview

This guide explains how to set up AWS IAM permissions for the document generation application to work with S3 versioning and object tagging.

### Quick Summary

To use the S3 document generation system, your AWS IAM user needs 7 specific S3 permissions. This guide walks you through setting them up.

---

## 🔐 Complete IAM Policy

### For Bucket: `amzn-rag-doc-generator`

This is the **recommended production policy** that includes all necessary permissions:

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketVersions",
        "s3:GetObjectVersion",
        "s3:PutBucketVersioning",
        "s3:PutObjectTagging"
      ],
      "Resource": [
        "arn:aws:s3:::amzn-rag-doc-generator",
        "arn:aws:s3:::amzn-rag-doc-generator/*"
      ]
    }
  ]
}
```

---

## 📖 Permissions Breakdown

| Permission | Purpose | Required For |
|-----------|---------|--------------|
| **s3:PutObject** | Upload documents to S3 bucket | Core upload functionality |
| **s3:GetObject** | Read documents from S3 | Version retrieval, verification |
| **s3:ListBucket** | List current objects in bucket | Manifest generation, verification |
| **s3:ListBucketVersions** | See all version history | Version reporting, audit trails |
| **s3:GetObjectVersion** | Retrieve specific document versions | Version access, rollback capability |
| **s3:PutBucketVersioning** | Enable/configure versioning on bucket | First-time setup only |
| **s3:PutObjectTagging** | Add tags to objects *(optional)* | Enhanced searchability, metadata tagging |

### Critical vs Optional

- **Critical** (6 permissions): Core functionality - application won't work without these
- **Optional** (1 permission): Enhanced features - application works without tagging permission, but logs warnings

---

## 🚀 Step-by-Step Setup

### Prerequisites
- AWS Account with admin access (to create policies)
- IAM User already created (e.g., `rag-document-user`)
- S3 Bucket already created (e.g., `amzn-rag-doc-generator`)

### Steps

#### Step 1: Open AWS IAM Console

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. In the left sidebar, click **Users**
3. Find and click your user (e.g., `rag-document-user`)

#### Step 2: Add Inline Policy

1. Click the **Permissions** tab
2. Click **Add permissions** → **Create inline policy**
3. Click the **JSON** tab
4. Clear the default content and paste the policy from above

#### Step 3: Review Policy

The policy should show:
- ✅ 7 actions listed
- ✅ 2 resources (bucket + bucket/*)
- ✅ Effect: Allow

#### Step 4: Apply Policy

1. Click **Review policy**
2. Enter a name: `S3DocumentGenerationPolicy`
3. Click **Create policy**

#### Step 5: Verify Installation

Wait 30 seconds, then verify:

```bash
export AWS_ACCESS_KEY_ID='your_access_key'
export AWS_SECRET_ACCESS_KEY='your_secret_key'

python3 << 'EOF'
import boto3
s3 = boto3.client('s3', region_name='us-east-1')

permissions = {
    's3:PutObject': False,
    's3:GetObject': False,
    's3:ListBucket': False,
    's3:ListBucketVersions': False,
    's3:GetObjectVersion': False,
    's3:PutBucketVersioning': False,
    's3:PutObjectTagging': False,
}

bucket = 'amzn-rag-doc-generator'

try:
    s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
    permissions['s3:ListBucket'] = True
except: pass

try:
    s3.list_object_versions(Bucket=bucket, MaxKeys=1)
    permissions['s3:ListBucketVersions'] = True
except: pass

try:
    s3.put_object(Bucket=bucket, Key='test.txt', Body=b'test')
    permissions['s3:PutObject'] = True
    s3.delete_object(Bucket=bucket, Key='test.txt')
except: pass

try:
    s3.get_bucket_versioning(Bucket=bucket)
    permissions['s3:PutBucketVersioning'] = True
except: pass

try:
    s3.put_object_tagging(
        Bucket=bucket, 
        Key='any_key',
        Tagging={'TagSet': [{'Key': 'test', 'Value': 'test'}]}
    )
    permissions['s3:PutObjectTagging'] = True
except: pass

print("\n✅ Permission Status:\n")
for perm, status in permissions.items():
    icon = "✅" if status else "❌"
    print(f"  {icon} {perm}")

all_granted = all(permissions.values())
if all_granted:
    print("\n✅ All permissions granted! Ready to proceed.")
else:
    print("\n⚠️ Some permissions missing. Review IAM policy.")
EOF
```

---

## 🔍 Troubleshooting

### Policy Not Taking Effect Immediately

**Issue**: Policy applied but permissions still denied  
**Reason**: IAM changes can take 30-60 seconds to propagate  
**Solution**: Wait 1 minute and retry

### Policy Applied but Tagging Still Fails

**Issue**: Tagging permission denied despite policy  
**Reason**: Policy scoped incorrectly or not applied to correct user  
**Solution**: 
1. Verify you're editing the correct IAM user
2. Check that policy has `arn:aws:s3:::amzn-rag-doc-generator/*` (with `/*`)
3. Verify no other policies are blocking tagging

### "Access Denied" for All Operations

**Issue**: Cannot upload, list, or read any objects  
**Reason**: Policy not applied or syntax error  
**Solution**:
1. Go to IAM user → Permissions tab
2. Look for policy named `S3DocumentGenerationPolicy`
3. Click it and verify all 7 actions are present
4. If policy missing, create it again

### Bucket Versioning Not Enabled

**Issue**: Upload works but no version history  
**Reason**: `s3:PutBucketVersioning` permission missing  
**Solution**: 
1. Add `s3:PutBucketVersioning` to policy
2. Re-run generation (app will enable versioning automatically)

---

## 🎯 Minimal Policy (Critical Only)

If you want **only** the critical permissions (no tagging):

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketVersions",
        "s3:GetObjectVersion",
        "s3:PutBucketVersioning"
      ],
      "Resource": [
        "arn:aws:s3:::amzn-rag-doc-generator",
        "arn:aws:s3:::amzn-rag-doc-generator/*"
      ]
    }
  ]
}
```

**Result**: Application works but tagging warnings appear in logs  
**Recommendation**: Add `s3:PutObjectTagging` for production use

---

## 📊 Verification Checklist

After setup, verify:

```
☐ IAM user created in AWS
☐ S3 bucket created (amzn-rag-doc-generator)
☐ Inline policy created named "S3DocumentGenerationPolicy"
☐ Policy contains all 7 actions
☐ Policy resources scoped to amzn-rag-doc-generator
☐ Policy applied to correct IAM user
☐ Waited 30+ seconds for propagation
☐ Verification script shows all permissions ✅
☐ Test upload successful
☐ S3 versioning automatically enabled
☐ Objects appear in bucket with correct metadata
```

---

## 🚀 Next Steps

1. ✅ Verify all permissions are granted (use verification script above)
2. ✅ Run document generation: `python3 app.py --days 5 --s3-bucket amzn-rag-doc-generator`
3. ✅ Verify documents in S3: Use [S3_OBJECTS_VERIFICATION.md](./S3_OBJECTS_VERIFICATION.md)
4. ✅ Check version history is working
5. ✅ Monitor logs for any permission warnings

---

## 📞 Support

For issues:
1. Check [TROUBLESHOOTING_TAGGING.md](./TROUBLESHOOTING_TAGGING.md)
2. Verify IAM policy syntax is exact JSON (no extra commas)
3. Confirm bucket name matches exactly in policy and code
4. Re-run verification script to pinpoint which permission is failing

---

*Last updated: August 3, 2026*
