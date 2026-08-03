"""S3 storage backend with document versioning support."""
import json
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3DocumentStorage:
    """Manages document storage in S3 with automatic versioning."""

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        enable_versioning: bool = True,
    ):
        """Initialize S3 storage client.

        Args:
            bucket_name: S3 bucket name for document storage
            region: AWS region
            enable_versioning: Enable S3 object versioning
        """
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client("s3", region_name=region)

        if enable_versioning:
            self._enable_bucket_versioning()

    def _enable_bucket_versioning(self) -> None:
        """Enable versioning on the S3 bucket."""
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={"Status": "Enabled"},
            )
            logger.info(f"Versioning enabled for bucket: {self.bucket_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] != "BucketAlreadyExists":
                logger.warning(f"Could not enable versioning: {e}")

    def upload_document(
        self,
        doc_id: str,
        content: str,
        day: int,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Upload a document to S3 with versioning metadata.

        Args:
            doc_id: Document identifier
            content: Document content
            day: Day snapshot number
            metadata: Additional metadata to store

        Returns:
            Upload result with version info
        """
        if metadata is None:
            metadata = {}

        # Build S3 key path: docs/{day}/{doc_id}
        s3_key = f"docs/day{day}/{doc_id}.txt"

        # Prepare versioning metadata
        version_metadata = {
            "doc_id": doc_id,
            "day": day,
            "uploaded_at": datetime.utcnow().isoformat(),
            "content_length": len(content),
            **metadata,
        }

        try:
            # Upload object without tags first (tagging may require additional permissions)
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode("utf-8"),
                ContentType="text/plain",
                Metadata={
                    "doc-id": doc_id,
                    "day": str(day),
                    "uploaded-at": version_metadata["uploaded_at"],
                },
            )

            version_id = response.get("VersionId")

            # Try to add tags (optional - if user lacks permission, log and continue)
            try:
                self.s3_client.put_object_tagging(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Tagging={
                        "TagSet": [
                            {"Key": "doc_id", "Value": doc_id},
                            {"Key": "day", "Value": str(day)},
                            {"Key": "versioned", "Value": "true"},
                        ]
                    },
                )
            except ClientError as tag_error:
                logger.warning(
                    f"Could not add tags to {s3_key}: {tag_error}. "
                    "Object uploaded successfully but without tags."
                )

            result = {
                "success": True,
                "s3_key": s3_key,
                "version_id": version_id,
                "metadata": version_metadata,
                "etag": response.get("ETag"),
            }
            logger.info(f"Uploaded {doc_id} to s3://{self.bucket_name}/{s3_key} (v{version_id})")
            return result

        except ClientError as e:
            logger.error(f"Failed to upload {doc_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "doc_id": doc_id,
            }

    def get_document_versions(self, doc_id: str) -> list[dict]:
        """Retrieve all versions of a document.

        Args:
            doc_id: Document identifier

        Returns:
            List of version records sorted by date (newest first)
        """
        versions = []
        try:
            # List all objects with doc_id in the key
            paginator = self.s3_client.get_paginator("list_object_versions")
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=f"docs/"):
                for version in page.get("Versions", []):
                    if f"/{doc_id}.txt" in version["Key"]:
                        versions.append(
                            {
                                "version_id": version.get("VersionId"),
                                "key": version["Key"],
                                "last_modified": version["LastModified"].isoformat(),
                                "size": version["Size"],
                                "is_latest": version.get("IsLatest", False),
                            }
                        )
        except ClientError as e:
            logger.error(f"Failed to retrieve versions for {doc_id}: {e}")

        # Sort by date, newest first
        return sorted(versions, key=lambda v: v["last_modified"], reverse=True)

    def get_document_version(
        self, doc_id: str, version_id: Optional[str] = None
    ) -> Optional[dict]:
        """Retrieve a specific version of a document.

        Args:
            doc_id: Document identifier
            version_id: Specific version ID (None for latest)

        Returns:
            Document content and metadata, or None if not found
        """
        try:
            # Find the key for this doc_id
            paginator = self.s3_client.get_paginator("list_object_versions")
            matching_key = None
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix="docs/"):
                for version in page.get("Versions", []):
                    if f"/{doc_id}.txt" in version["Key"]:
                        matching_key = version["Key"]
                        break
                if matching_key:
                    break

            if not matching_key:
                logger.warning(f"Document {doc_id} not found in S3")
                return None

            # Fetch the specific version
            get_params = {"Bucket": self.bucket_name, "Key": matching_key}
            if version_id:
                get_params["VersionId"] = version_id

            response = self.s3_client.get_object(**get_params)

            return {
                "doc_id": doc_id,
                "content": response["Body"].read().decode("utf-8"),
                "version_id": response.get("VersionId"),
                "last_modified": response["LastModified"].isoformat(),
                "size": response["ContentLength"],
                "metadata": response.get("Metadata", {}),
            }

        except ClientError as e:
            logger.error(f"Failed to retrieve version for {doc_id}: {e}")
            return None

    def upload_manifest(self, day: int, manifest_content: str) -> dict:
        """Upload day's manifest to S3.

        Args:
            day: Day snapshot number
            manifest_content: Manifest file content

        Returns:
            Upload result
        """
        s3_key = f"manifests/day{day}/manifest.txt"

        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=manifest_content.encode("utf-8"),
                ContentType="text/plain",
                Metadata={"day": str(day), "uploaded-at": datetime.utcnow().isoformat()},
            )

            result = {
                "success": True,
                "s3_key": s3_key,
                "version_id": response.get("VersionId"),
            }
            logger.info(f"Uploaded manifest for day {day} to {s3_key}")
            return result

        except ClientError as e:
            logger.error(f"Failed to upload manifest for day {day}: {e}")
            return {"success": False, "error": str(e)}

    def upload_documents_batch(
        self, day: int, documents: list[tuple[str, str]], manifest_content: str
    ) -> dict:
        """Upload all documents and manifest for a day atomically.

        Args:
            day: Day snapshot number
            documents: List of (doc_id, content) tuples
            manifest_content: Manifest file content

        Returns:
            Summary of upload results
        """
        results = {
            "day": day,
            "documents": [],
            "manifest": None,
            "total_uploaded": 0,
            "total_failed": 0,
        }

        # Upload all documents
        for doc_id, content in documents:
            result = self.upload_document(doc_id, content, day)
            results["documents"].append(result)
            if result.get("success"):
                results["total_uploaded"] += 1
            else:
                results["total_failed"] += 1

        # Upload manifest
        manifest_result = self.upload_manifest(day, manifest_content)
        results["manifest"] = manifest_result

        return results

    def create_version_tag(self, doc_id: str, tag_name: str) -> dict:
        """Create a named version tag for easy reference.

        Args:
            doc_id: Document identifier
            tag_name: Version tag name (e.g., "approved", "draft")

        Returns:
            Tag creation result
        """
        versions = self.get_document_versions(doc_id)
        if not versions:
            return {"success": False, "error": f"No versions found for {doc_id}"}

        latest = versions[0]  # Most recent version
        tag_key = f"version-tags/{doc_id}/{tag_name}.json"

        tag_data = {
            "doc_id": doc_id,
            "tag_name": tag_name,
            "version_id": latest["version_id"],
            "s3_key": latest["key"],
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=tag_key,
                Body=json.dumps(tag_data).encode("utf-8"),
                ContentType="application/json",
            )
            logger.info(f"Created tag '{tag_name}' for {doc_id}")
            return {"success": True, "tag_key": tag_key, "tag_data": tag_data}

        except ClientError as e:
            logger.error(f"Failed to create tag '{tag_name}' for {doc_id}: {e}")
            return {"success": False, "error": str(e)}

    def generate_version_report(self, doc_id: str) -> Optional[dict]:
        """Generate a comprehensive version report for a document.

        Args:
            doc_id: Document identifier

        Returns:
            Version report with all metadata
        """
        versions = self.get_document_versions(doc_id)
        if not versions:
            return None

        latest = self.get_document_version(doc_id)
        if not latest:
            return None

        return {
            "doc_id": doc_id,
            "total_versions": len(versions),
            "latest_version": {
                "version_id": latest["version_id"],
                "last_modified": latest["last_modified"],
                "size": latest["size"],
            },
            "all_versions": versions,
            "first_version": versions[-1] if versions else None,
        }


def get_s3_storage(
    bucket_name: Optional[str] = None,
    region: Optional[str] = None,
) -> S3DocumentStorage:
    """Factory function to create S3DocumentStorage with env var support.

    Args:
        bucket_name: S3 bucket name (uses env var if not provided)
        region: AWS region (uses env var if not provided)

    Returns:
        S3DocumentStorage instance
    """
    bucket = bucket_name or os.getenv("DOCS_S3_BUCKET", "documents-churn")
    aws_region = region or os.getenv("AWS_REGION", "us-east-1")

    return S3DocumentStorage(bucket_name=bucket, region=aws_region)
