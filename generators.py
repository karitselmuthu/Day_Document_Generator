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
    platform = rng.choice(platforms)
    cloud_context = platform_resource_context[platform]

    payload = {
        "duration_ms": rng.randint(15, 1500),
        "retry_count": rng.randint(0, 3),
        "shard_id": f"shard-{rng.randint(1, 16):02d}",
        "message": "Synthetic operational event for workload monitoring.",
        "recovery_action": rng.choice(actions),
    }

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
        "payload": payload,
    }
    return json.dumps(log_record, ensure_ascii=True, indent=2)


def generate_regulatory_framework(rng: random.Random) -> str:
    frameworks = [
        ("BCBS 239", "Banking risk data aggregation and reporting controls."),
        ("IFRS 17", "Insurance contract recognition, measurement, and disclosure."),
        ("PCI-DSS", "Cardholder data protection and secure processing standards."),
    ]
    framework, summary = rng.choice(frameworks)
    return f"""Document ID: REG-{rng.randint(100,999)}
Type: Regulatory Framework
Framework: {framework}
Summary: {summary}

Mandatory Controls:
1. Data lineage must be traceable from source systems to reporting outputs.
2. Exceptions require documented risk acceptance and expiry date.
3. Quarterly control attestations are required from process owners.
4. Breaches must be reported to compliance governance within 24 hours.

Evidence Required:
- Control execution logs
- Policy acknowledgements
- Audit trail snapshots
- Corrective action plans"""


def generate_audit_report(rng: random.Random) -> str:
    titles = [
        "Quarterly Internal Controls Review",
        "External Compliance Assurance Letter",
        "Access Governance Audit Findings",
    ]
    root_causes = [
        "Outdated privileged access recertification workflow",
        "Incomplete encryption key rotation evidence",
        "Delayed incident closure after policy exception approval",
    ]
    return f"""Document ID: AUD-{rng.randint(100,999)}
Type: Audit Report
Title: {rng.choice(titles)}
Audit Period: 2026-Q{rng.randint(1,4)}
Severity Mix: High={rng.randint(0,2)}, Medium={rng.randint(2,6)}, Low={rng.randint(3,8)}

Findings:
- Root Cause: {rng.choice(root_causes)}
- Impact: Regulatory reporting quality may degrade under peak transaction load.
- Recommendation: Enforce preventive controls in CI/CD and IAM workflows.
- Target Date: 2026-{rng.randint(1,12):02d}-15

Management Response:
Control owners accepted findings and committed remediation milestones."""


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

Tables:
1. accounts(account_id PK, customer_id, status, opened_at, risk_tier)
2. transactions(txn_id PK, account_id FK, amount, currency, channel, created_at)
3. claims(claim_id PK, policy_id, claimant_id, status, reserve_amount, submitted_at)
4. audit_events(event_id PK, entity_type, entity_id, actor_id, action, event_ts)

Security Metadata:
- accounts.customer_id encrypted with AES-256 at rest.
- transactions.amount masked in non-production replicas.
- audit_events retained for 7 years and immutable by design.

Indexing Notes:
- btree on transactions(account_id, created_at)
- gin on audit_events(action)
- partial index on claims(status) where status in ('open', 'investigating')"""


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
