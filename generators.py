import datetime
import json
import random
from typing import Callable

CATEGORIES = [
    "log",
    "regulatory_framework",
    "audit_report",
    "kyc_aml_guideline",
    "data_privacy_notice",
    "product_disclosure_statement",
    "fee_schedule",
    "claims_investigation_report",
    "standard_operating_procedure",
    "chat_call_transcript",
    "faq",
    "customer_complaint_file",
    "api_specification",
    "architecture_topology",
    "runbook_postmortem",
    "database_schema",
]


def _random_hex(rng: random.Random, length: int) -> str:
    alphabet = "0123456789abcdef"
    return "".join(rng.choice(alphabet) for _ in range(length))


def generate_log(rng: random.Random, now_fn: Callable[[], datetime.datetime]) -> str:
    platforms = ["Datacenter", "Azure VM", "AWS EKS"]
    platform_resource_context = {
        "Datacenter": {
            "account_id": "dc-001",
            "region": "onprem-primary",
            "cluster_name": "dc-core-cluster",
        },
        "Azure VM": {
            "account_id": "azure-prod-8492",
            "region": "eastus2",
            "cluster_name": "aks-insurance-prod",
        },
        "AWS EKS": {
            "account_id": "aws-prod-7145",
            "region": "ap-south-1",
            "cluster_name": "eks-claims-prod",
        },
    }
    apps = ["InsurancePortal", "ClaimsProcessing", "PolicyManagement"]
    levels = ["INFO", "WARN", "ERROR"]
    components = ["auth-service", "claim-worker", "policy-api", "document-parser"]
    namespaces = ["claims-prod", "policy-prod", "insurance-shared"]
    pods = [
        "claim-worker-6f94d6b6f5-2gv7k",
        "policy-api-775f95f9b4-s9wr2",
        "auth-service-5445f74666-d8j9t",
    ]
    actions = [
        "retried transaction after timeout and completed successfully",
        "rejected request because role mapping was missing",
        "loaded policy bundle into in-memory cache",
        "detected stale session token and triggered re-auth flow",
    ]
    error_codes = [
        ("403", "AUTHORIZATION_ERROR", "role_mapping_missing"),
        ("504", "SERVICE_UNAVAILABLE", "downstream_timeout"),
        ("500", "INTERNAL_ERROR", "cache_inconsistency"),
        ("429", "RATE_LIMIT", "quota_exceeded"),
    ]
    
    platform = rng.choice(platforms)
    cloud_context = platform_resource_context[platform]
    http_code, error_type, reason = rng.choice(error_codes)

    # Performance metrics for RAG chunking
    performance_metrics = {
        "cpu_usage_percent": rng.randint(15, 85),
        "memory_used_mb": rng.randint(256, 1024),
        "gc_pause_ms": rng.randint(5, 150),
        "db_query_time_ms": rng.randint(10, 500),
        "cache_hit_rate": round(rng.uniform(0.5, 0.99), 3),
    }
    
    # Diagnostic fields
    diagnostics = {
        "circuit_breaker_state": rng.choice(["CLOSED", "OPEN", "HALF_OPEN"]),
        "downstream_service": rng.choice(["policy-cache-layer", "auth-service", "claims-db"]),
        "request_queue_depth": rng.randint(5, 200),
        "active_connections": rng.randint(50, 500),
    }

    payload = {
        "duration_ms": rng.randint(15, 1500),
        "retry_count": rng.randint(0, 3),
        "shard_id": f"shard-{rng.randint(1, 16):02d}",
        "message": "Synthetic operational event for workload monitoring.",
        "recovery_action": rng.choice(actions),
        "http_status_code": http_code,
        "error_type": error_type,
        "error_reason": reason,
    }

    # Context narrative for RAG
    context_narrative = f"""
CONTEXT NARRATIVE:
The {error_type} ({http_code}) error occurred in {cloud_context['cluster_name']} when attempting to process a
transaction through the {rng.choice(components)} component. The system detected {diagnostics['downstream_service']} 
was unresponsive with {diagnostics['circuit_breaker_state']} circuit breaker state. 

Related Systems:
- Cross-reference: AUD-{rng.randint(100,999)} (Audit findings on cache invalidation policies)
- Cross-reference: DBS-{rng.randint(100,999)} (Database schema for role_mappings table)

Risk Assessment:
- Current cache_hit_rate: {performance_metrics['cache_hit_rate']} (threshold: 0.85)
- Request queue depth: {diagnostics['request_queue_depth']} (threshold: 100)
- Service recovery time: ~{rng.randint(30, 300)} seconds

Resolution Path:
1. Verify {diagnostics['downstream_service']} health status and restart if degraded
2. Check role_mappings table consistency (DBS-{rng.randint(100,999)})
3. Clear in-memory cache and reload from authoritative source
4. Monitor circuit breaker transitions for 15 minutes
5. Escalate to on-call if condition persists beyond RTO threshold of 60 minutes
"""

    log_record = {
        "document_id": f"LOG-{rng.randint(100,999)}",
        "type": "log",
        "timestamp": now_fn().isoformat(),
        "severity": rng.choice(levels),
        "application": rng.choice(apps),
        "component": rng.choice(components),
        "trace_id": _random_hex(rng, 32),
        "span_id": _random_hex(rng, 16),
        "cloud": {
            "platform": platform,
            "resource": cloud_context,
        },
        "k8s": {
            "k8s.pod.name": rng.choice(pods),
            "k8s.namespace.name": rng.choice(namespaces),
        },
        "performance_metrics": performance_metrics,
        "diagnostics": diagnostics,
        "payload": payload,
        "context_narrative": context_narrative,
    }
    return json.dumps(log_record, ensure_ascii=True, indent=2)


def generate_regulatory_framework(rng: random.Random) -> str:
    frameworks = [
        ("BCBS 239", "Banking risk data aggregation and reporting controls.", "Prudential Authority", 2013),
        ("IFRS 17", "Insurance contract recognition, measurement, and disclosure.", "IASB", 2023),
        ("PCI-DSS 4.0", "Cardholder data protection and secure processing standards.", "PCI Council", 2024),
    ]
    framework, summary, authority, year = rng.choice(frameworks)
    
    compliance_table = """
| Control Area | Requirement | Compliance Status | Evidence | Review Date |
| --- | --- | --- | --- | --- |
| Data Lineage | Traceable from source to reporting | Compliant | Audit trail logs | 2026-Q3 |
| Exception Management | Documented risk acceptance + expiry | In Progress | Policy exception log | 2026-Q2 |
| Attestations | Quarterly control owner sign-off | Compliant | Signed attestations | Monthly |
| Breach Notification | Report to governance within 24h | Compliant | Incident tickets | As-needed |
"""
    
    return f"""Document ID: REG-{rng.randint(100,999)}
Type: Regulatory Framework
Framework: {framework}
Issuing Authority: {authority}
Year Adopted: {year}
Effective Date: 2026-01-01

FRAMEWORK SUMMARY:
{summary}

Applicability: Mandatory for all financial services operations processing customer data 
or managing risk exposure in {rng.choice(['EMEA', 'APAC', 'Americas'])} regions.

MANDATORY CONTROLS:

1. Data Lineage & Auditability
   - All data transformations must be traceable from source systems to reporting outputs
   - Requirement: Complete audit trail with timestamps and actor identification
   - RAG Cross-Reference: DBS-{rng.randint(100,999)} (audit_events table design)
   - Implementation: audit_events table with immutable JSONB change tracking
   - Monitoring: Automated daily verification of lineage integrity

2. Exception Management Framework
   - Policy exceptions require:
     • Documented risk acceptance by authorized stakeholder
     • Clear expiry date (max 90 days without renewal)
     • Auto-closure event triggering cache invalidation
   - RAG Cross-Reference: AUD-{rng.randint(100,999)} (F-001 policy exception findings)
   - Database: policy_exceptions table with state machine management
   - SQS Integration: Publish to policy-event-stream on APPROVED status

3. Control Attestation Program
   - Quarterly certification by process owners required
   - Controls: authentication, authorization, audit trails, encryption
   - Escalation: Any attestation gaps flagged to governance committee
   - Testing: Automated and manual control execution testing

4. Breach Notification Protocol
   - Security incidents must be reported to compliance governance within 24 hours
   - Criteria: Unauthorized access, data exposure, service disruption
   - Reporting: Incident ticket with trace_id linking to operational logs
   - RAG Cross-Reference: LOG-{rng.randint(100,999)} (trace_id correlation)

COMPLIANCE STATUS MATRIX:
{compliance_table}

EVIDENCE REQUIREMENTS:

Documentation Package:
- Control execution logs (generated by automated systems)
- Policy acknowledgements (digital signatures from stakeholders)
- Audit trail snapshots (quarterly extracts from audit_events table)
- Corrective action plans (linked to audit findings via AUD-* documents)

Archival & Retention:
- Evidence retained for {rng.choice(['7', '10'])} years
- Immutable storage in compliance data lake
- Regular integrity verification via checksums

ENFORCEMENT & PENALTIES:

Non-Compliance Consequences:
- First violation: Written warning + 30-day remediation deadline
- Repeated violations: Regulatory sanctions (financial) + operational restrictions
- Severe breaches: Escalation to financial regulator + public disclosure

CROSS-FRAMEWORK MAPPING:

This framework aligns with:
- ISO 27001:2022 (Information Security Management)
- SOC 2 Type II (Service Organization Controls)
- GDPR Article 5 (Data integrity and confidentiality)
- FCA Senior Management Regime (UK Handbook Requirement)

Compliance Officer: {rng.choice(['Alice Johnson', 'Bob Smith', 'Carol Williams'])}
Last Review: 2026-{rng.randint(1,8):02d}-{rng.randint(1,28):02d}
Next Review: 2026-{rng.randint(9,12):02d}-{rng.randint(1,28):02d}"""


def generate_audit_report(rng: random.Random) -> str:
    titles = [
        "Quarterly Internal Controls Review",
        "External Compliance Assurance Letter",
        "Access Governance Audit Findings",
    ]
    components = ["Policy Exception", "RBAC Cache", "CI/CD Pipeline", "Database Access", "Service Account Provisioning"]
    severities = ["HIGH", "MEDIUM", "LOW"]
    
    # Generate 11 audit findings for RAG chunking
    findings = []
    for i in range(1, 12):
        finding = {
            "id": f"F-{i:03d}",
            "severity": rng.choice(severities),
            "component": rng.choice(components),
            "root_cause": f"Component {i % len(components)} misconfiguration or policy gap",
            "impact": f"Affects ~{rng.randint(50, 300)} requests/sec with {rng.randint(5, 30)}min RTO",
            "target_date": f"2026-{rng.randint(6,12):02d}-{rng.randint(1,28):02d}"
        }
        findings.append(finding)
    
    # Build findings table
    findings_table = "| Finding ID | Severity | Component | Root Cause | Impact | Target Date |\n"
    findings_table += "| --- | --- | --- | --- | --- | --- |\n"
    for f in findings:
        findings_table += f"| {f['id']} | {f['severity']} | {f['component']} | {f['root_cause'][:40]}... | {f['impact'][:50]}... | {f['target_date']} |\n"
    
    # Root cause analysis
    rca_narrative = f"""
ROOT CAUSE ANALYSIS (F-001 & F-002 Interconnection):
Finding F-001 (Policy Exception management) and F-002 (RBAC Cache staleness) are interconnected:
- Policy exceptions created manually without triggering cache invalidation events
- Result: Cached role_mappings become stale, leading to 403 authorization errors (see LOG-{rng.randint(100,999)})
- Database schema inadequacy: role_mappings table lacks event_subscription fields (see DBS-{rng.randint(100,999)})
- Impact: ~300+ req/sec affected with 15min RTO during peak hours

PREVENTIVE CONTROLS:
1. Implement Event Integration Layer: SQS topic for policy exceptions with encryption
2. Add authentication/authorization layer for event producers
3. Implement cache invalidation subscribers in policy-cache-layer
4. Add monitoring dashboard tracking exception-to-invalidation latency
"""

    # Phased remediation plan
    remediation_plan = """
PHASED REMEDIATION PLAN:

Phase 1: Event Integration Layer (4 weeks target)
- Design: Create SQS topic (policy-event-stream) with encryption
- Implementation: Add authentication for event producers
- Testing: Unit tests for event payload validation
- Completion: 2026-Q3 Week 2

Phase 2: System Integration (4 weeks target)
- Connect incident management system to policy-event-stream
- Add cache layer subscribers for automatic invalidation
- Implement SLA targets: exception-to-invalidation within 30 seconds
- Completion: 2026-Q3 Week 4

Phase 3: Testing & Rollout (4 weeks target)
- Canary deployment to 10% traffic
- Load testing: simulate 500 req/sec with continuous exception flow
- Validate cache hit rate maintains >0.85 threshold
- SLA targets: P99 latency <200ms, cache consistency 99.99%
- Completion: 2026-Q3 Week 8
"""

    # Compliance mapping
    compliance_table = """
| Compliance Framework | Applicable | Evidence Required | Status |
| --- | --- | --- | --- |
| SOC 2 Type II | Yes | Change management audit trail | Tracking |
| ISO 27001:2022 | Yes | Access control attestation | In Progress |
| FCA Senior Management Regime | Yes | Risk governance documentation | Scheduled |
"""

    return f"""Document ID: AUD-{rng.randint(100,999)}
Type: Audit Report
Title: {rng.choice(titles)}
Audit Period: 2026-Q{rng.randint(1,4)}
Audit Date: {rng.choice(['2026-08-15', '2026-07-20', '2026-09-10'])}

EXECUTIVE SUMMARY:
Audit identified {sum(1 for f in findings if f['severity'] == 'HIGH')} HIGH severity findings requiring immediate remediation. 
Key interconnected issues between policy exception management and cache layer consistency pose operational risk.

{findings_table}

{rca_narrative}

{remediation_plan}

COMPLIANCE MAPPING:
{compliance_table}

METRICS & MONITORING:
- Exception-to-cache-invalidation latency: Target <30 seconds (P95)
- Cache hit rate threshold: >0.85 (alert if <0.80)
- Authorization error rate: <0.1% of total requests
- Dashboard: Grafana dashboard tracking all metrics in real-time

CROSS-REFERENCES:
- Related incident: LOG-{rng.randint(100,999)} (403 authorization error example)
- Database design: DBS-{rng.randint(100,999)} (role_mappings and policy_exceptions schema)

Management Response:
Control owners accepted findings and committed to phased remediation milestones through Q3 2026."""


def generate_kyc_aml_guideline(rng: random.Random) -> str:
    risk_tiers = ["low", "medium", "high"]
    return f"""Document ID: KYC-{rng.randint(100,999)}
Type: KYC / AML Guideline
Version: 3.{rng.randint(0,9)}

Workflow:
1. Capture customer identity document, proof of address, and tax identifier.
2. Validate name, date of birth, and address across trusted data providers.
3. Screen against sanctions, PEP, and adverse media watchlists.
4. Assign risk tier ({rng.choice(risk_tiers)}) and choose due diligence depth.
5. Escalate suspicious indicators to AML case management within 2 hours.
6. Store evidence package for 7 years with immutable audit history.

Suspicious Activity Triggers:
- Repeated transfers just below reporting threshold.
- Mismatch between declared occupation and transaction behavior.
- Third-party cash deposit patterns across unrelated accounts."""


def generate_data_privacy_notice(rng: random.Random) -> str:
    jurisdictions = ["GDPR", "CCPA"]
    return f"""Document ID: PRIV-{rng.randint(100,999)}
Type: Data Privacy Notice
Jurisdiction: {rng.choice(jurisdictions)}
Retention Policy: Customer profile data retained for 7 years after account closure.

Customer Rights:
1. Right to access personal data and processing rationale.
2. Right to request correction of inaccurate records.
3. Right to request deletion subject to legal retention obligations.
4. Right to restrict or object to certain processing activities.
5. Right to receive exportable copy of personal data.

Processing Purposes:
- Fraud prevention and transaction risk scoring
- Claims lifecycle servicing and legal compliance
- Product personalization and service quality analytics"""


def generate_product_disclosure_statement(rng: random.Random) -> str:
    products = ["Auto Insurance Plus", "Home Shield Premium", "Health Secure Plan"]
    return f"""Document ID: PDS-{rng.randint(100,999)}
Type: Product Disclosure Statement
Product: {rng.choice(products)}

Coverage Matrix:
| Section | Coverage Item | Limit (USD) | Excess (USD) | Exclusion |
| --- | --- | ---: | ---: | --- |
| A | Accidental Damage | {rng.randint(10000,50000)} | {rng.randint(100,500)} | Wear and tear |
| B | Third Party Liability | {rng.randint(50000,250000)} | {rng.randint(200,1000)} | Intentional acts |
| C | Medical Reimbursement | {rng.randint(5000,30000)} | {rng.randint(50,300)} | Non-prescribed treatment |

Premium Rules:
- Base premium adjusted by risk score, claim history, and geography.
- Monthly payment surcharge applies when annual payment is not selected.
- Material non-disclosure may void cover or reduce claim payout."""


def generate_fee_schedule(rng: random.Random) -> str:
    return f"""Document ID: FEE-{rng.randint(100,999)}
Type: Fee Schedule
Currency: USD
Effective Date: 2026-{rng.randint(1,12):02d}-01

Charges:
| Fee Type | Amount | Rule | Notes |
| --- | ---: | --- | --- |
| Monthly Account Maintenance | {rng.randint(5,20)}.00 | Waived if balance > 5000 | Retail checking |
| Overdraft Penalty | {rng.randint(25,45)}.00 | Max 1 per day | Does not apply to declined transaction |
| Domestic Wire Transfer | {rng.randint(10,30)}.00 | Per successful transfer | Same-day settlement |
| International Wire Transfer | {rng.randint(20,55)}.00 | FX margin applies | Compliance review required |
| Paper Statement | {rng.randint(2,8)}.00 | Per month | Free for senior accounts |

Interest Rates:
- Savings Tier 1: 1.25%
- Savings Tier 2: 2.10%
- Unsecured Overdraft APR: 19.75%"""


def generate_claims_investigation_report(rng: random.Random) -> str:
    indicators = [
        "inconsistent timeline between incident report and geolocation data",
        "duplicate invoice identifiers across unrelated providers",
        "abnormal claim frequency within 90-day period",
    ]
    return f"""Document ID: CIR-{rng.randint(100,999)}
Type: Claims Investigation Report
Claim Reference: CLM-{rng.randint(100000,999999)}
Policyholder Segment: {rng.choice(["retail", "commercial", "corporate"])}

Case Summary:
Adjuster reviewed supporting evidence, transaction history, and third-party records.
Primary fraud indicator observed: {rng.choice(indicators)}.

Evidence Review:
1. Interview notes reconciled with claim submission metadata.
2. Medical/repair documentation validated against provider registries.
3. Prior claim overlap assessed using internal entity resolution.

Recommendation:
Route case to fraud desk for secondary review before payout authorization."""


def generate_standard_operating_procedure(rng: random.Random) -> str:
    domains = ["branch teller cash operations", "loan underwriting", "back-office settlement"]
    return f"""Document ID: SOP-{rng.randint(100,999)}
Type: Standard Operating Procedure
Domain: {rng.choice(domains)}
Version: 2.{rng.randint(0,9)}

Procedure Steps:
1. Validate request ticket and confirm customer consent artifacts.
2. Verify control checkpoints in workflow system before processing.
3. Execute transaction in core platform and capture reference ID.
4. Perform dual-control verification for high-risk actions.
5. Send completion notification and archive case evidence.

Quality Controls:
- Supervisor sampling: 10% of daily processed cases.
- SLA target: 95% completion within 30 minutes.
- Escalation threshold: any unresolved exception over 2 hours."""


def generate_chat_call_transcript(rng: random.Random) -> str:
    channels = ["chat", "call"]
    return f"""Document ID: CX-{rng.randint(100,999)}
Type: Anonymized Support Transcript
Channel: {rng.choice(channels)}
Case ID: CASE-{rng.randint(10000,99999)}

Transcript:
[00:00] Customer: My transfer failed twice and I was still charged a fee.
[00:18] Agent: I can help. Let me verify the transaction reference and account status.
[01:12] Customer: I need the payment processed today for a medical emergency.
[02:05] Agent: I have reversed the duplicate fee and escalated the transfer to priority queue.
[03:20] Customer: Please confirm if this impacts my fraud alert status.
[03:48] Agent: No fraud block is active; you will receive SMS confirmation in 10 minutes.

Outcome:
Issue resolved with fee reversal and same-day transfer confirmation."""


def generate_faq(rng: random.Random) -> str:
    faq_pairs = [
        (
            "Why was my card payment declined even though funds are available?",
            "The payment may fail due to merchant category restrictions, risk rules, or network timeout. Retry once and contact support with reference ID if it fails again.",
        ),
        (
            "How long does claim reimbursement take after document submission?",
            "Standard reimbursement is processed within 7 business days after all mandatory documents are validated.",
        ),
        (
            "Can I increase my transfer limit for one high-value transaction?",
            "Yes. A temporary limit increase can be approved after enhanced identity verification and purpose-of-transfer confirmation.",
        ),
    ]
    q1, a1 = rng.choice(faq_pairs)
    q2, a2 = rng.choice(faq_pairs)
    return f"""Document ID: FAQ-{rng.randint(100,999)}
Type: Frequently Asked Questions

Q1: {q1}
A1: {a1}

Q2: {q2}
A2: {a2}
"""


def generate_customer_complaint_file(rng: random.Random) -> str:
    issues = [
        "unauthorized overdraft fee after failed transfer",
        "delayed claim settlement beyond published SLA",
        "incorrect risk flag causing account service interruption",
    ]
    return f"""Document ID: CMP-{rng.randint(100,999)}
Type: Customer Complaint File
Complaint ID: OMB-{rng.randint(100000,999999)}

Complaint Summary:
Customer submitted formal grievance citing {rng.choice(issues)}.

Remediation Steps:
1. Complaint acknowledged within 24 hours and assigned case owner.
2. Root cause analysis completed with evidence from transaction logs.
3. Financial correction processed where customer detriment confirmed.
4. Preventive action added to control register and tracked to closure.

Closure Criteria:
Customer receives written explanation, resolution details, and escalation options."""


def generate_api_specification(rng: random.Random) -> str:
    operations = [
        ("/payments/transfer", "post", "Create payment transfer"),
        ("/claims/submit", "post", "Submit insurance claim"),
        ("/accounts/{accountId}/limits", "patch", "Update account transfer limits"),
    ]
    path, method, description = rng.choice(operations)
    return f"""Document ID: API-{rng.randint(100,999)}
Type: API Specification
Format: OpenAPI 3.0 (excerpt)

openapi: 3.0.3
info:
  title: Financial Services Internal API
  version: "1.9"
paths:
  {path}:
    {method}:
      summary: {description}
      operationId: op_{rng.randint(1000,9999)}
      responses:
        "200":
          description: Success
        "400":
          description: Validation error
        "403":
          description: Authorization failure
components:
  securitySchemes:
    oauth2:
      type: oauth2"""


def generate_architecture_topology(rng: random.Random) -> str:
    return f"""Document ID: ARC-{rng.randint(100,999)}
Type: Architecture Topology

Environment Overview:
- Edge: API Gateway with WAF and bot filtering
- Compute: EKS workloads across {rng.choice(["2", "3"])} availability zones
- Data: PostgreSQL primary with cross-region read replicas
- Messaging: Event bus for claims and payments asynchronous workflows

Network Boundaries:
1. Public subnet hosts ingress and TLS termination only.
2. Private subnet hosts application pods and internal services.
3. Restricted subnet hosts databases, KMS proxies, and vault services.

Resilience:
- RPO target: 15 minutes
- RTO target: 60 minutes
- Automated failover drill cadence: monthly"""


def generate_runbook_postmortem(rng: random.Random) -> str:
    return f"""Document ID: PRM-{rng.randint(100,999)}
Type: Runbook and Post-Mortem
Incident ID: INC-{rng.randint(100000,999999)}
Severity: SEV-{rng.choice([1, 2, 3])}

Detection and Timeline:
- T+00m: Alert fired for elevated payment API latency.
- T+07m: On-call confirmed pod restart storm in claims namespace.
- T+19m: Traffic shifted to standby node group.
- T+38m: Service recovered and backlog drained.

Root Cause:
Misconfigured resource limit triggered cascading OOM kills after release deployment.

Runbook Actions:
1. Freeze deployments and scale healthy node pool.
2. Restore last known good manifest and validate readiness probes.
3. Reprocess failed transactions from dead-letter queue.

Follow-up:
Add policy guardrails to block invalid resource limit configurations."""


def generate_database_schema(rng: random.Random) -> str:
    return f"""Document ID: DBS-{rng.randint(100,999)}
Type: Database Schema
System: Core Financial Ledger
Engine: PostgreSQL 14
Last Updated: 2026-08-03

SCHEMA OVERVIEW:
This comprehensive database supports multi-tenant insurance and financial services operations with 
full audit trails, encryption, and state machine management for complex workflows.

TABLE DEFINITIONS:

1. ACCOUNTS TABLE
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| account_id | UUID | PRIMARY KEY | Unique account identifier |
| customer_id | UUID | FOREIGN KEY | References customers table |
| status | ENUM | NOT NULL | ACTIVE, INACTIVE, SUSPENDED, CLOSED |
| account_type | VARCHAR | NOT NULL | RETAIL, COMMERCIAL, CORPORATE |
| opened_at | TIMESTAMP | NOT NULL | Account creation timestamp |
| closed_at | TIMESTAMP | NULL | Account closure timestamp |
| risk_tier | VARCHAR | DEFAULT 'MEDIUM' | LOW, MEDIUM, HIGH classification |
| last_review_date | DATE | NULL | Last risk review date |
| created_by | VARCHAR | NOT NULL | Service account or user ID |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last modification timestamp |

Encryption: customer_id encrypted with AES-256-GCM (KMS rotation: monthly)
Indexes: btree(account_id), btree(customer_id), btree(status), partial(status='ACTIVE')

2. TRANSACTIONS TABLE
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| txn_id | UUID | PRIMARY KEY | Unique transaction identifier |
| account_id | UUID | FOREIGN KEY | References accounts table |
| amount | DECIMAL(15,2) | NOT NULL, CHECK(>0) | Transaction amount in currency |
| currency | VARCHAR | NOT NULL DEFAULT 'USD' | ISO 4217 currency code |
| channel | VARCHAR | NOT NULL | MOBILE_APP, WEB, ATM, BRANCH |
| txn_type | VARCHAR | NOT NULL | TRANSFER, WITHDRAWAL, DEPOSIT, PAYMENT |
| reference_id | VARCHAR | UNIQUE | Idempotency key for duplicate prevention |
| created_by | VARCHAR | NOT NULL | Initiator: user_id or service_id |
| created_at | TIMESTAMP | NOT NULL | Transaction timestamp |
| settlement_date | DATE | NULL | Cleared date for settlement |
| status | VARCHAR | NOT NULL | PENDING, COMPLETED, FAILED, CANCELLED |

Encryption: amount masked in non-production replicas
Indexes: btree(account_id, created_at), btree(created_at), btree(reference_id)
GIN Index: gin(channel, txn_type) for composite queries

3. CLAIMS TABLE
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| claim_id | UUID | PRIMARY KEY | Unique claim identifier |
| policy_id | UUID | FOREIGN KEY | References policies table |
| claimant_id | UUID | FOREIGN KEY | References customers table |
| status | VARCHAR | NOT NULL | SUBMITTED, INVESTIGATING, APPROVED, REJECTED, SETTLED |
| state_transition_ts | TIMESTAMP | NOT NULL | Last state change timestamp |
| reserve_amount | DECIMAL(15,2) | NOT NULL, CHECK(>0) | Financial reserve set |
| approved_amount | DECIMAL(15,2) | NULL | Amount approved for payout |
| settlement_date | DATE | NULL | Date claim was settled |
| submitted_at | TIMESTAMP | NOT NULL | Initial submission timestamp |
| investigator_id | VARCHAR | NULL | Assigned investigator user_id |
| priority_level | VARCHAR | NOT NULL DEFAULT 'NORMAL' | URGENT, NORMAL, LOW |

Encryption: claimant_id encrypted AES-256, claim_id cleartext for audit linking
Triggers: Updates audit_events on every status change, manages state machine transitions
Indexes: btree(policy_id), btree(claimant_id), btree(status), partial(status IN ('SUBMITTED', 'INVESTIGATING'))

4. AUDIT_EVENTS TABLE
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| event_id | UUID | PRIMARY KEY | Unique event identifier |
| entity_type | VARCHAR | NOT NULL | ACCOUNT, TRANSACTION, CLAIM, POLICY |
| entity_id | UUID | NOT NULL | References entity being audited |
| actor_id | VARCHAR | NOT NULL | User, service account, or system |
| action | VARCHAR | NOT NULL | CREATE, UPDATE, DELETE, APPROVE, REJECT |
| reason | TEXT | NULL | Justification for sensitive actions |
| result_status | VARCHAR | NOT NULL | SUCCESS, FAILURE, PARTIAL |
| event_ts | TIMESTAMP | NOT NULL | Event timestamp (NOT modifiable) |
| trace_id | VARCHAR | NULL | OpenTelemetry trace for correlation |
| change_tracking | JSONB | NULL | Before/after field values for updates |

Immutability: audit_events is immutable by design (no UPDATE/DELETE permitted)
Retention: 7-year retention for regulatory compliance
Indexes: gin(action), btree(event_ts), btree(entity_type, entity_id), btree(trace_id)

5. POLICY_EXCEPTIONS TABLE (NEW)
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| exception_id | UUID | PRIMARY KEY | Policy exception identifier |
| policy_id | UUID | FOREIGN KEY | References policies table |
| exception_type | VARCHAR | NOT NULL | RATE_OVERRIDE, COVERAGE_WAIVER, RENEWAL_DELAY |
| status | VARCHAR | NOT NULL | REQUESTED, APPROVED, EXPIRED, REVOKED |
| created_by | VARCHAR | NOT NULL | Exception requester |
| created_at | TIMESTAMP | NOT NULL | Request timestamp |
| approved_by | VARCHAR | NULL | Approver user_id |
| approved_at | TIMESTAMP | NULL | Approval timestamp |
| expiry_date | DATE | NOT NULL | Auto-closure date |
| auto_closure_event_id | UUID | NULL | References audit_events for closure |
| cache_invalidation_event_id | UUID | NULL | References SQS event triggering cache clear |

State Machine: REQUESTED → APPROVED → EXPIRED (auto) or REVOKED (manual)
Triggers: On APPROVED state, publish event to SQS topic 'policy-event-stream'
Indexes: btree(policy_id), btree(status), btree(expiry_date), partial(status='APPROVED')

6. ROLE_MAPPINGS TABLE (NEW)
| Column Name | Type | Constraint | Notes |
| --- | --- | --- | --- |
| mapping_id | UUID | PRIMARY KEY | Mapping identifier |
| service_account_id | VARCHAR | NOT NULL, UNIQUE | Service account name |
| role_bindings | JSONB | NOT NULL | Array of roles: ['ADMIN', 'USER', 'VIEWER'] |
| cache_state | VARCHAR | NOT NULL DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, PENDING_CACHE_INVALIDATION |
| last_synced_at | TIMESTAMP | NOT NULL | Last sync with authoritative source |
| sqs_event_id | VARCHAR | NULL | Links to SQS invalidation event |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

RAG Link: role_mappings stale cache causes LOG-{rng.randint(100,999)} (403 errors)
SQS Trigger: When cache_invalidation_event_id published, all subscribers with cache_state='PENDING_CACHE_INVALIDATION' reload
Indexes: unique(service_account_id), btree(cache_state), gin(role_bindings)

SECURITY METADATA:

Encryption at Rest:
- Algorithm: AES-256-GCM
- Key Management: AWS KMS with customer-managed CMK
- Rotation Policy: Monthly automated rotation
- Encrypted Columns: customer_id, claimant_id, sensitive JSONB fields

Encryption in Transit:
- Protocol: TLS 1.3 mandatory for all database connections
- Certificate Validation: Enabled, hostname verification required
- Perfect Forward Secrecy: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384

Row-Level Security (RLS) Policies:
- accounts: Only queries by customer_id owner or ADMIN role
- transactions: Service accounts see only filtered by account_id scope
- claims: Investigators see only assigned claims (investigator_id match)
- audit_events: Immutable; append-only for regulatory trail

Access Control:
- Service Accounts: policy-cache-layer, claims-processor, transaction-processor
- DBA Role: schema maintenance, index tuning, emergency procedures
- Analytics Role: SELECT-only on production replicas
- Application Role: CRUD on assigned tables only

DATA RETENTION & ARCHIVAL POLICIES:

| Table | Retention Period | Archival | Notes |
| --- | --- | --- | --- |
| accounts | 7 years after closure | S3 quarterly snapshots | Regulatory requirement |
| transactions | 7 years | Parquet files to Data Lake | Reconstruct ledger capability |
| claims | 10 years | Archive to Glacier after 2 years | Insurance compliance |
| audit_events | 7 years (immutable) | Never delete | Regulatory trail |
| policy_exceptions | 3 years | Move to cold storage | Reference only |
| role_mappings | 1 year | Delete after verification | Cache refresh capability |

DATA QUALITY & CONSTRAINTS:

Referential Integrity:
- accounts.customer_id → customers.customer_id (CASCADE on customer delete)
- transactions.account_id → accounts.account_id (RESTRICT, prevent orphans)
- claims.policy_id → policies.policy_id (RESTRICT)
- policy_exceptions.policy_id → policies.policy_id (CASCADE)

Check Constraints:
- transactions: amount > 0
- claims: reserve_amount > 0, reserve_amount >= approved_amount
- accounts: opened_at <= closed_at
- audit_events: event_ts <= NOW() (prevent future dates)

PERFORMANCE TUNING STRATEGY:

Query Patterns Matched to Indexes:
- "Get all transactions for account since date": btree(account_id, created_at) DESC LIMIT 100
- "Find claims by investigator": btree(investigator_id, status)
- "Audit trail for entity": btree(entity_type, entity_id, event_ts)
- "Search by text fields": gin(action) for full-text search

Vacuum & ANALYZE Schedule:
- Nightly: VACUUM ANALYZE on high-churn tables (transactions, audit_events)
- Weekly: Full maintenance window for index bloat cleanup
- Month-End: REINDEX all tables before financial close

Connection Pooling (PgBouncer):
- Pool Size: 50 connections per service
- Timeout: 30 seconds idle, 5 minutes max age
- Alert Thresholds: Queue depth >10, connection wait >1 second

CROSS-REFERENCES FOR RAG INTEGRATION:

Related Operational Logs:
- LOG-{rng.randint(100,999)}: Example 403 error from stale role_mappings cache
- Diagnostic: circuit_breaker_state, downstream_service = "policy-cache-layer"

Related Audit Findings:
- AUD-{rng.randint(100,999)}: Audit Report with F-001 (Policy Exception) and F-002 (RBAC Cache)
- Finding interconnection: policy_exceptions lack event subscribers → stale cache → 403 errors

Integration Points:
- auth-service: Reads role_mappings on every authorization decision
- policy-cache-layer: Subscribes to SQS policy-event-stream for invalidation
- incident-management: Publishes to SQS when exception approved (auto_closure_event_id)

Deployment Timestamp: 2026-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}T{rng.randint(8,18):02d}:00:00Z"""


def generate_documents(
    n: int,
    rng: random.Random,
    now_fn: Callable[[], datetime.datetime],
) -> list[str]:
    docs: list[str] = []
    for _ in range(n):
        category = rng.choice(CATEGORIES)
        if category == "log":
            docs.append(generate_log(rng, now_fn))
        elif category == "regulatory_framework":
            docs.append(generate_regulatory_framework(rng))
        elif category == "audit_report":
            docs.append(generate_audit_report(rng))
        elif category == "kyc_aml_guideline":
            docs.append(generate_kyc_aml_guideline(rng))
        elif category == "data_privacy_notice":
            docs.append(generate_data_privacy_notice(rng))
        elif category == "product_disclosure_statement":
            docs.append(generate_product_disclosure_statement(rng))
        elif category == "fee_schedule":
            docs.append(generate_fee_schedule(rng))
        elif category == "claims_investigation_report":
            docs.append(generate_claims_investigation_report(rng))
        elif category == "standard_operating_procedure":
            docs.append(generate_standard_operating_procedure(rng))
        elif category == "chat_call_transcript":
            docs.append(generate_chat_call_transcript(rng))
        elif category == "faq":
            docs.append(generate_faq(rng))
        elif category == "customer_complaint_file":
            docs.append(generate_customer_complaint_file(rng))
        elif category == "api_specification":
            docs.append(generate_api_specification(rng))
        elif category == "architecture_topology":
            docs.append(generate_architecture_topology(rng))
        elif category == "runbook_postmortem":
            docs.append(generate_runbook_postmortem(rng))
        elif category == "database_schema":
            docs.append(generate_database_schema(rng))
    return docs
