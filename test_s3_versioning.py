"""Test suite for S3 storage and versioning functionality.

This module demonstrates and tests the document versioning capabilities.
"""
import unittest
from unittest.mock import MagicMock, patch, call
import json
from datetime import datetime


class TestS3DocumentStorage(unittest.TestCase):
    """Test S3 storage operations and versioning."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock boto3 to avoid requiring AWS credentials in tests
        self.s3_patcher = patch("s3_storage.boto3")
        self.mock_boto3 = self.s3_patcher.start()

        self.mock_s3_client = MagicMock()
        self.mock_boto3.client.return_value = self.mock_s3_client

    def tearDown(self):
        """Clean up patches."""
        self.s3_patcher.stop()

    def test_upload_document_creates_versioning_metadata(self):
        """Test that document uploads include proper versioning metadata."""
        from s3_storage import S3DocumentStorage

        # Mock S3 response
        self.mock_s3_client.put_object.return_value = {
            "VersionId": "abc123xyz789"
        }

        storage = S3DocumentStorage(bucket_name="test-bucket")
        result = storage.upload_document(
            doc_id="LOG-123",
            content="Test log content",
            day=1,
            metadata={"source": "system_logs"}
        )

        # Verify upload was successful
        self.assertTrue(result["success"])
        self.assertEqual(result["version_id"], "abc123xyz789")
        self.assertEqual(result["s3_key"], "docs/day1/LOG-123.txt")

        # Verify metadata was included
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Bucket"], "test-bucket")
        self.assertIn("doc-id", call_args[1]["Metadata"])
        self.assertEqual(call_args[1]["Metadata"]["doc-id"], "LOG-123")
        self.assertEqual(call_args[1]["Metadata"]["day"], "1")

    def test_batch_upload_maintains_order(self):
        """Test that batch uploads maintain document order."""
        from s3_storage import S3DocumentStorage

        self.mock_s3_client.put_object.return_value = {
            "VersionId": "v1234567890"
        }

        storage = S3DocumentStorage(bucket_name="test-bucket")

        docs = [
            ("DOC-001", "Content 1"),
            ("DOC-002", "Content 2"),
            ("DOC-003", "Content 3"),
        ]

        manifest = "index\tdocument_id\n001\tDOC-001\n002\tDOC-002\n003\tDOC-003"

        result = storage.upload_documents_batch(day=1, documents=docs, manifest_content=manifest)

        # Verify all documents were uploaded
        self.assertEqual(result["total_uploaded"], 3)
        self.assertEqual(result["total_failed"], 0)
        self.assertEqual(len(result["documents"]), 3)

        # Verify upload order
        upload_calls = self.mock_s3_client.put_object.call_args_list
        # First 3 calls are documents, 4th is manifest
        for i, doc_id in enumerate(["DOC-001", "DOC-002", "DOC-003"]):
            args = upload_calls[i][1]
            self.assertIn(doc_id, args["Key"])

    def test_version_tagging_creates_tag_metadata(self):
        """Test that version tags include proper metadata."""
        from s3_storage import S3DocumentStorage

        # Mock list_object_versions response
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "Versions": [
                    {
                        "Key": "docs/day1/LOG-123.txt",
                        "VersionId": "v1234567890",
                        "LastModified": datetime.now(),
                        "Size": 1024,
                        "IsLatest": True,
                    }
                ]
            }
        ]

        self.mock_s3_client.put_object.return_value = {}

        storage = S3DocumentStorage(bucket_name="test-bucket")
        result = storage.create_version_tag("LOG-123", "approved")

        # Verify tag was created
        self.assertTrue(result["success"])

        # Verify tag contains version metadata
        call_args = self.mock_s3_client.put_object.call_args
        tag_data = json.loads(call_args[1]["Body"].decode())
        self.assertEqual(tag_data["doc_id"], "LOG-123")
        self.assertEqual(tag_data["tag_name"], "approved")
        self.assertEqual(tag_data["version_id"], "v1234567890")

    def test_version_history_sorted_by_date(self):
        """Test that version history is sorted newest first."""
        from s3_storage import S3DocumentStorage

        # Mock version history
        mock_versions = [
            {
                "Key": "docs/day1/LOG-123.txt",
                "VersionId": "v1",
                "LastModified": datetime(2026, 8, 1),
                "Size": 1024,
                "IsLatest": False,
            },
            {
                "Key": "docs/day3/LOG-123.txt",
                "VersionId": "v3",
                "LastModified": datetime(2026, 8, 3),
                "Size": 2048,
                "IsLatest": True,
            },
            {
                "Key": "docs/day2/LOG-123.txt",
                "VersionId": "v2",
                "LastModified": datetime(2026, 8, 2),
                "Size": 1536,
                "IsLatest": False,
            },
        ]

        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Versions": mock_versions}
        ]

        storage = S3DocumentStorage(bucket_name="test-bucket")
        versions = storage.get_document_versions("LOG-123")

        # Verify sorting (newest first)
        self.assertEqual(len(versions), 3)
        self.assertEqual(versions[0]["version_id"], "v3")
        self.assertEqual(versions[1]["version_id"], "v2")
        self.assertEqual(versions[2]["version_id"], "v1")

    def test_get_document_version_by_version_id(self):
        """Test retrieving a specific document version."""
        from s3_storage import S3DocumentStorage

        # Mock version list
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "Versions": [
                    {
                        "Key": "docs/day1/LOG-123.txt",
                        "VersionId": "v1",
                        "LastModified": datetime.now(),
                        "Size": 1024,
                        "IsLatest": False,
                    }
                ]
            }
        ]

        # Mock get_object response
        self.mock_s3_client.get_object.return_value = {
            "Body": MagicMock(read=lambda: b"Version 1 content"),
            "VersionId": "v1",
            "LastModified": datetime.now(),
            "ContentLength": 1024,
            "Metadata": {"doc-id": "LOG-123"},
        }

        storage = S3DocumentStorage(bucket_name="test-bucket")
        doc = storage.get_document_version("LOG-123", version_id="v1")

        # Verify document content
        self.assertIsNotNone(doc)
        self.assertEqual(doc["content"], "Version 1 content")
        self.assertEqual(doc["doc_id"], "LOG-123")
        self.assertEqual(doc["version_id"], "v1")

    def test_document_update_creates_new_version(self):
        """Test that updating a document creates a new version."""
        from s3_storage import S3DocumentStorage

        version_ids = ["v1", "v2"]
        call_count = [0]

        def mock_put_object(**kwargs):
            vid = version_ids[call_count[0]]
            call_count[0] += 1
            return {"VersionId": vid}

        self.mock_s3_client.put_object.side_effect = mock_put_object

        storage = S3DocumentStorage(bucket_name="test-bucket")

        # First upload
        result1 = storage.upload_document("LOG-123", "Version 1", day=1)
        self.assertEqual(result1["version_id"], "v1")

        # Second upload (update)
        result2 = storage.upload_document("LOG-123", "Version 1 Updated", day=1)
        self.assertEqual(result2["version_id"], "v2")

        # Verify different versions
        self.assertNotEqual(result1["version_id"], result2["version_id"])


class TestVersioningWorkflow(unittest.TestCase):
    """Test complete versioning workflows."""

    def test_daily_document_lifecycle(self):
        """Test document lifecycle across multiple days with versioning."""
        scenario = {
            "day1": {
                "LOG-001": "Initial log entry",
                "REG-001": "Regulatory framework v1",
                "AUD-001": "Audit report v1",
            },
            "day2": {
                "LOG-001": "Log entry updated",  # Updated
                "REG-001": "Regulatory framework v1",  # Unchanged
                # AUD-001 retired (not in day2)
                "API-001": "API specification",  # New
            },
            "day3": {
                "LOG-001": "Log entry final update",  # Updated again
                "API-001": "API specification updated",  # Updated
                "REG-001": "Regulatory framework v1",  # Unchanged
                "CMP-001": "Customer complaint",  # New
            },
        }

        expected_versions = {
            "LOG-001": 3,  # v1 (day1), v2 (day2), v3 (day3)
            "REG-001": 1,  # v1 (day1, unchanged)
            "AUD-001": 1,  # v1 (day1, retired in day2)
            "API-001": 2,  # v1 (day2), v2 (day3)
            "CMP-001": 1,  # v1 (day3)
        }

        # This demonstrates the expected versioning behavior
        for doc_id, expected_count in expected_versions.items():
            print(f"\n{doc_id}: Expected {expected_count} version(s)")

    def test_version_tag_workflow(self):
        """Test creating and managing version tags."""
        tags_workflow = {
            "LOG-001": {
                "v1": ["draft"],  # Initial version is draft
                "v2": ["draft"],  # Update is draft
                "v3": ["approved", "production"],  # Final version approved
            },
            "REG-001": {
                "v1": ["draft", "review"],  # Awaiting review
            },
        }

        # This demonstrates the expected tag workflow
        for doc_id, versions in tags_workflow.items():
            for version_id, tags in versions.items():
                print(f"\n{doc_id} {version_id}: Tags: {', '.join(tags)}")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
