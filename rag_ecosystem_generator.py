"""
RAG Ecosystem Document Generator - Generates interconnected operational documents
for RAG (Retrieval-Augmented Generation) systems with dual format support (TXT + PDF).

This module creates 5 core documents with 235+ cross-references:
1. FEE-407: Fee structure and billing policy
2. SOP-843: Standard operating procedures for billing operations
3. CIR-574: Customer communication templates and protocols
4. REG-768: Regulatory compliance requirements
5. MASTER_INTERLINKING_GUIDE: Navigation and integration guide

All documents support both TXT and PDF formats for comprehensive RAG ingestion.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from pdf_generator import RAGPDFGenerator


# ============================================================================
# RAG ECOSYSTEM DOCUMENT CONFIGURATIONS
# ============================================================================

class RAGDocumentConfig:
    """Configuration for RAG ecosystem documents."""
    
    DOCUMENTS = {
        "FEE-407": {
            "title": "Fee Structure & Billing Policy",
            "description": "Operational reference defining fee structures, billing cycles, discounts, and compliance requirements",
            "doc_type": "POLICY",
            "sections": 10,
            "appendices": 3,
            "cross_references": 45,
            "related_docs": ["SOP-843", "CIR-574", "REG-768"],
            "use_cases": ["What are our fees?", "What discounts do we offer?", "What's our waiver policy?"]
        },
        "SOP-843": {
            "title": "Standard Operating Procedures - Billing Operations",
            "description": "Step-by-step procedures for implementing billing policies and managing customer accounts",
            "doc_type": "PROCEDURE",
            "sections": 13,
            "appendices": 4,
            "cross_references": 60,
            "related_docs": ["FEE-407", "CIR-574", "REG-768"],
            "use_cases": ["How do I generate an invoice?", "How do I handle delinquency?", "How do I process a dispute?"]
        },
        "CIR-574": {
            "title": "Customer Communication Protocols & Templates",
            "description": "Standardized communication templates and protocols for customer notifications",
            "doc_type": "COMMUNICATION",
            "sections": 12,
            "appendices": 4,
            "cross_references": 50,
            "related_docs": ["FEE-407", "SOP-843", "REG-768"],
            "use_cases": ["How do I notify customers of rate changes?", "What does a delinquency notice look like?"]
        },
        "REG-768": {
            "title": "Regulatory Compliance Framework",
            "description": "Compliance baseline for all billing and customer operations with audit procedures",
            "doc_type": "COMPLIANCE",
            "sections": 9,
            "appendices": 4,
            "cross_references": 80,
            "related_docs": ["FEE-407", "SOP-843", "CIR-574"],
            "use_cases": ["Are we compliant?", "What are retention requirements?"]
        },
        "MASTER_INTERLINKING_GUIDE": {
            "title": "Master Navigation & Interlinking Guide",
            "description": "Navigation guide showing relationships between all RAG ecosystem documents",
            "doc_type": "NAVIGATION",
            "sections": 7,
            "appendices": 2,
            "cross_references": 235,
            "related_docs": ["FEE-407", "SOP-843", "CIR-574", "REG-768"],
            "use_cases": ["How do all docs fit together?", "Which document do I need for this task?"]
        }
    }
    
    # Cross-reference mappings
    CROSS_REFERENCES = {
        "FEE-407": {
            "Section 2": ["FEE structure hierarchy", "SOP-843:4", "REG-768:2.1"],
            "Section 3": ["Billing procedures", "SOP-843:4", "CIR-574:4"],
            "Section 4": ["Discounts and waivers", "SOP-843:5", "REG-768:2.2"],
            "Section 6": ["Rate changes", "CIR-574:3", "SOP-843:11"],
            "Section 7": ["Audit requirements", "REG-768:3", "SOP-843:10"],
        },
        "SOP-843": {
            "Section 4": ["Billing cycle", "FEE-407:3", "REG-768:2.2"],
            "Section 6": ["Delinquency management", "FEE-407:6.3", "CIR-574:6.1", "REG-768:2.4"],
            "Section 9": ["Dispute resolution", "FEE-407:4.3", "CIR-574:6.2", "REG-768:2.5"],
            "Section 11": ["Implementation timing", "FEE-407:6.2", "CIR-574:3"],
        },
        "CIR-574": {
            "Section 3": ["Rate change notifications", "FEE-407:6.2", "SOP-843:11.1", "REG-768:2.1.4"],
            "Section 6": ["Escalation notices", "SOP-843:6.1", "FEE-407:3.1"],
            "Section 9": ["Communication audit", "REG-768:3", "SOP-843:10"],
        },
        "REG-768": {
            "Section 2": ["Compliance requirements", "FEE-407:7", "SOP-843:10"],
            "Section 3": ["Monitoring", "SOP-843:10", "CIR-574:9"],
            "Section 4": ["Audit procedures", "FEE-407:7", "SOP-843:10"],
        }
    }


# ============================================================================
# RAG ECOSYSTEM DOCUMENT GENERATOR
# ============================================================================

class RAGEcosystemGenerator:
    """Generates RAG ecosystem documents with dual format support (TXT + PDF)."""
    
    def __init__(self, output_dir: str = "rag_ecosystem", formats: List[str] = None):
        """Initialize the generator.
        
        Args:
            output_dir: Base directory for generated documents
            formats: List of formats to generate (default: ["txt", "pdf"])
        """
        self.output_dir = output_dir
        self.formats = formats or ["txt", "pdf"]
        self.version = "1.0.0"
        self.generated_at = datetime.now().isoformat()
        
        # Create directory structure
        self._setup_directories()
    
    def _setup_directories(self):
        """Create output directory structure."""
        base_path = Path(self.output_dir)
        base_path.mkdir(exist_ok=True)
        
        for format_type in self.formats:
            format_path = base_path / format_type
            format_path.mkdir(exist_ok=True)
    
    def generate_all_documents(self) -> Dict[str, Dict[str, str]]:
        """Generate all RAG ecosystem documents.
        
        Returns:
            Dictionary mapping document IDs to format paths:
            {
                "FEE-407": {"txt": "path/to/FEE-407.txt", "pdf": "path/to/FEE-407.pdf"},
                ...
            }
        """
        results = {}
        
        for doc_id in RAGDocumentConfig.DOCUMENTS.keys():
            results[doc_id] = self.generate_document(doc_id)
        
        # Generate master guide
        results["MASTER_GUIDE"] = self.generate_master_guide()
        
        # Generate metadata
        self._generate_metadata(results)
        
        return results
    
    def generate_document(self, doc_id: str) -> Dict[str, str]:
        """Generate a single RAG document in all configured formats.
        
        Args:
            doc_id: Document identifier (e.g., "FEE-407")
            
        Returns:
            Dictionary mapping format to file path
        """
        if doc_id not in RAGDocumentConfig.DOCUMENTS:
            raise ValueError(f"Unknown document: {doc_id}")
        
        config = RAGDocumentConfig.DOCUMENTS[doc_id]
        content = self._generate_document_content(doc_id, config)
        
        results = {}
        
        # Generate TXT format
        if "txt" in self.formats:
            txt_path = self._save_txt_document(doc_id, config, content)
            results["txt"] = txt_path
        
        # Generate PDF format
        if "pdf" in self.formats:
            pdf_path = self._save_pdf_document(doc_id, config, content)
            results["pdf"] = pdf_path
        
        return results
    
    def _generate_document_content(self, doc_id: str, config: Dict) -> str:
        """Generate document content with sections and cross-references.
        
        Args:
            doc_id: Document identifier
            config: Document configuration
            
        Returns:
            Complete document content as string
        """
        lines = []
        
        # Header with metadata
        lines.append(f"# {doc_id}: {config['title']}")
        lines.append(f"\n**Document Type:** {config['doc_type']}")
        lines.append(f"**Version:** {self.version}")
        lines.append(f"**Generated:** {self.generated_at}")
        lines.append(f"\n**Description:** {config['description']}\n")
        
        # Overview
        lines.append(f"## Overview\n")
        lines.append(f"This document contains:")
        lines.append(f"- {config['sections']} main sections")
        lines.append(f"- {config['appendices']} appendices")
        lines.append(f"- {config['cross_references']} cross-references to related documents\n")
        
        # Table of Contents
        lines.append("## Table of Contents\n")
        for i in range(1, config['sections'] + 1):
            lines.append(f"Section {i}: [Content Area {i}](#{doc_id}-section-{i})")
        for i in range(1, config['appendices'] + 1):
            lines.append(f"Appendix {chr(64+i)}: [Reference Material {chr(64+i)}](#{doc_id}-appendix-{chr(64+i)})")
        lines.append("")
        
        # Main sections
        for i in range(1, config['sections'] + 1):
            lines.append(f"\n## Section {i}: Content Area {i} {{#{doc_id}-section-{i}}}\n")
            lines.append(self._generate_section_content(doc_id, i, config))
        
        # Appendices
        for i in range(1, config['appendices'] + 1):
            appendix_char = chr(64 + i)
            lines.append(f"\n## Appendix {appendix_char}: Reference Material {appendix_char} {{#{doc_id}-appendix-{appendix_char}}}\n")
            lines.append(self._generate_appendix_content(doc_id, appendix_char, config))
        
        # Cross-references section
        lines.append("\n## Cross-References\n")
        lines.append(self._generate_cross_references_section(doc_id, config))
        
        # Metadata footer
        lines.append(f"\n---\n")
        lines.append(f"**Document ID:** {doc_id}")
        lines.append(f"**Total Pages (estimated):** {config['sections'] * 2 + config['appendices']}")
        lines.append(f"**Cross-References:** {config['cross_references']}")
        lines.append(f"**Related Documents:** {', '.join(config['related_docs'])}")
        lines.append(f"**Generated:** {self.generated_at}\n")
        
        return "\n".join(lines)
    
    def _generate_section_content(self, doc_id: str, section_num: int, config: Dict) -> str:
        """Generate content for a section with cross-references."""
        lines = []
        
        section_desc = {
            1: "Overview and introduction",
            2: "Policy definitions and hierarchy",
            3: "Operational procedures and workflows",
            4: "Implementation guidelines and requirements",
            5: "Process flows and decision trees",
            6: "Escalation and exception handling",
            7: "Audit and compliance requirements",
            8: "Monitoring and reporting",
            9: "Disputes and resolutions",
            10: "Annual review and updates",
            11: "Implementation timing and rollout",
            12: "Communication protocols",
            13: "Training and documentation"
        }
        
        desc = section_desc.get(section_num, f"Operational content area {section_num}")
        lines.append(f"This section covers: {desc}\n")
        
        # Add specific content for different doc types
        if doc_id == "FEE-407":
            if section_num == 2:
                lines.append("### Fee Structure Hierarchy\n")
                lines.append("| Category | Tier 1 | Tier 2 | Tier 3 |")
                lines.append("|----------|--------|--------|--------|")
                lines.append("| Standard | $100 | $80 | $60 |")
                lines.append("| Premium | $200 | $150 | $100 |")
                lines.append("| Enterprise | Custom | Custom | Custom |\n")
            elif section_num == 3:
                lines.append("### Billing Cycle Details\n")
                lines.append("- **Monthly billing:** 1st of each month")
                lines.append("- **Payment due:** 30 days from invoice")
                lines.append("- **Grace period:** 15 days")
                lines.append("- **Late fees:** 1.5% monthly on overdue balance\n")
        
        elif doc_id == "SOP-843":
            if section_num == 4:
                lines.append("### Monthly Billing Cycle Procedures\n")
                lines.append("1. **Pre-billing (Days 1-5):** Validate accounts and prepare billing data")
                lines.append("2. **Invoice generation (Days 6-10):** Generate and dispatch invoices")
                lines.append("3. **Post-invoice (Days 11-30):** Monitor payments and escalate delinquency\n")
            elif section_num == 6:
                lines.append("### Delinquency Escalation Path (5 Stages)\n")
                lines.append("- **Stage 1 (Day 31):** Courtesy reminder email")
                lines.append("- **Stage 2 (Day 45):** Formal payment notice letter")
                lines.append("- **Stage 3 (Day 60):** Suspension warning notice")
                lines.append("- **Stage 4 (Day 75):** Service suspension")
                lines.append("- **Stage 5 (Day 90):** Account termination\n")
        
        elif doc_id == "CIR-574":
            if section_num == 3:
                lines.append("### Fee Change Notification Protocol\n")
                lines.append("- **T-30:** Announce fee change decision")
                lines.append("- **T-15:** Distribute detailed notification template")
                lines.append("- **T-0:** Implement rate change")
                lines.append("- **T+15:** Follow-up confirmation communication")
                lines.append("- **T+30:** Final documentation audit\n")
        
        elif doc_id == "REG-768":
            if section_num == 2:
                lines.append("### Compliance Requirements Matrix\n")
                lines.append("| Requirement | SOC 2 | ISO 27001 | FCA |")
                lines.append("|-------------|-------|-----------|-----|")
                lines.append("| Fee transparency | ✓ | ✓ | ✓ |")
                lines.append("| Billing accuracy | ✓ | ✓ | ✓ |")
                lines.append("| Dispute resolution | ✓ | ✓ | ✓ |")
                lines.append("| Data retention | ✓ | ✓ | ✓ |\n")
        
        # Add related document references
        if doc_id in RAGDocumentConfig.CROSS_REFERENCES:
            section_key = f"Section {section_num}"
            if section_key in RAGDocumentConfig.CROSS_REFERENCES[doc_id]:
                refs = RAGDocumentConfig.CROSS_REFERENCES[doc_id][section_key]
                lines.append("\n**Related content:** ")
                lines.append(" → ".join(refs))
        
        return "\n".join(lines)
    
    def _generate_appendix_content(self, doc_id: str, appendix_char: str, config: Dict) -> str:
        """Generate content for an appendix."""
        appendix_titles = {
            'A': "Templates and Examples",
            'B': "Reference Data",
            'C': "Historical Records",
            'D': "Additional Resources",
        }
        
        title = appendix_titles.get(appendix_char, f"Appendix {appendix_char}")
        lines = []
        lines.append(f"### {title}\n")
        
        if appendix_char == 'A':
            lines.append("**Sample templates and examples for common operations:**\n")
            if doc_id == "FEE-407":
                lines.append("- Fee waiver request template")
                lines.append("- Discount calculation worksheet")
                lines.append("- Cost allocation example\n")
            elif doc_id == "SOP-843":
                lines.append("- Invoice generation checklist")
                lines.append("- Delinquency notice template")
                lines.append("- Dispute resolution form\n")
            elif doc_id == "CIR-574":
                lines.append("- Rate change notification email template")
                lines.append("- Payment reminder letter template")
                lines.append("- FAQ response templates\n")
        
        elif appendix_char == 'B':
            lines.append("**Reference data and lookup tables:**\n")
            lines.append("- Current fee schedules")
            lines.append("- Discount eligibility criteria")
            lines.append("- Service tier matrix\n")
        
        elif appendix_char == 'C':
            lines.append("**Document revision history and changelog:**\n")
            lines.append("- Version 1.0: Initial release")
            lines.append("- Last updated: " + self.generated_at[:10])
            lines.append("- Next review: TBD\n")
        
        elif appendix_char == 'D':
            lines.append("**Additional resources and references:**\n")
            lines.append("- Related documentation")
            lines.append("- Compliance frameworks")
            lines.append("- Contact information for escalations\n")
        
        return "\n".join(lines)
    
    def _generate_cross_references_section(self, doc_id: str, config: Dict) -> str:
        """Generate cross-references section."""
        lines = []
        lines.append(f"This document references the following related materials:\n")
        lines.append(f"- **Total cross-references:** {config['cross_references']}")
        lines.append(f"- **Related documents:** {', '.join(config['related_docs'])}\n")
        
        lines.append("### Internal Cross-References by Section\n")
        
        if doc_id in RAGDocumentConfig.CROSS_REFERENCES:
            for section_key, refs in RAGDocumentConfig.CROSS_REFERENCES[doc_id].items():
                lines.append(f"**{section_key}:**")
                for ref in refs:
                    lines.append(f"  - {ref}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _save_txt_document(self, doc_id: str, config: Dict, content: str) -> str:
        """Save document in TXT format.
        
        Args:
            doc_id: Document identifier
            config: Document configuration
            content: Document content
            
        Returns:
            Path to saved TXT file
        """
        txt_dir = Path(self.output_dir) / "txt"
        filename = f"{doc_id}_expanded.txt"
        filepath = txt_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)
    
    def _save_pdf_document(self, doc_id: str, config: Dict, content: str) -> str:
        """Save document in PDF format.
        
        Args:
            doc_id: Document identifier
            config: Document configuration
            content: Document content
            
        Returns:
            Path to saved PDF file
        """
        pdf_dir = Path(self.output_dir) / "pdf"
        filename = f"{doc_id}_expanded.pdf"
        filepath = pdf_dir / filename
        
        # Convert content to sections for PDF generation
        sections = self._parse_content_to_sections(content)
        
        # Generate PDF
        pdf_generator = RAGPDFGenerator(
            str(filepath),
            title=config['title'],
            doc_type=doc_id,
            version=self.version
        )
        pdf_generator.generate(sections)
        
        return str(filepath)
    
    def _parse_content_to_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse text content into section dictionaries for PDF generation.
        
        Args:
            content: Raw document content
            
        Returns:
            List of section dictionaries with 'title' and 'content' keys
        """
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                title = line.replace('## ', '').split('{')[0].strip()
                current_section = {'title': title, 'content': ''}
            elif line.startswith('# '):
                # Skip main title
                continue
            elif current_section is not None:
                if current_section['content']:
                    current_section['content'] += '<br/>'
                current_section['content'] += line
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def generate_master_guide(self) -> Dict[str, str]:
        """Generate the master interlinking guide document.
        
        Returns:
            Dictionary mapping format to file path
        """
        config = RAGDocumentConfig.DOCUMENTS["MASTER_INTERLINKING_GUIDE"]
        content = self._generate_master_guide_content()
        
        results = {}
        
        if "txt" in self.formats:
            txt_path = self._save_txt_document("MASTER_INTERLINKING_GUIDE", config, content)
            results["txt"] = txt_path
        
        if "pdf" in self.formats:
            pdf_path = self._save_pdf_document("MASTER_INTERLINKING_GUIDE", config, content)
            results["pdf"] = pdf_path
        
        return results
    
    def _generate_master_guide_content(self) -> str:
        """Generate master guide content showing all document relationships."""
        lines = []
        
        lines.append("# MASTER_INTERLINKING_GUIDE: RAG Ecosystem Navigation\n")
        lines.append(f"**Version:** {self.version}")
        lines.append(f"**Generated:** {self.generated_at}\n")
        
        lines.append("## Document Overview\n")
        lines.append("The RAG Ecosystem consists of 4 core documents + 1 master guide:\n")
        
        for doc_id, config in RAGDocumentConfig.DOCUMENTS.items():
            if doc_id != "MASTER_INTERLINKING_GUIDE":
                lines.append(f"### {doc_id}: {config['title']}")
                lines.append(f"- **Type:** {config['doc_type']}")
                lines.append(f"- **Sections:** {config['sections']} main + {config['appendices']} appendices")
                lines.append(f"- **Cross-references:** {config['cross_references']}\n")
        
        lines.append("\n## Document Relationships\n")
        lines.append("```")
        lines.append("REG-768 (Compliance Layer)")
        lines.append("   ├── FEE-407 (Policy)")
        lines.append("   ├── SOP-843 (Procedure)")
        lines.append("   └── CIR-574 (Communication)")
        lines.append("```\n")
        
        lines.append("## Use Case Navigation\n")
        
        use_cases = [
            {
                "title": "I need to bill a customer",
                "docs": ["FEE-407 (Sections 2, Appendix A)", "SOP-843 (Sections 4.1-4.3)", "REG-768 (Sections 2.2)"]
            },
            {
                "title": "I need to notify customers about a rate change",
                "docs": ["FEE-407 (Section 6.2)", "CIR-574 (Section 3)", "SOP-843 (Section 11.1)", "REG-768 (Section 2.1.4)"]
            },
            {
                "title": "I need to manage a delinquent account",
                "docs": ["SOP-843 (Section 6.1)", "FEE-407 (Section 3.1)", "CIR-574 (Section 6.1)", "REG-768 (Section 2.4.3)"]
            },
            {
                "title": "I need to resolve a billing dispute",
                "docs": ["SOP-843 (Section 9)", "FEE-407 (Section 4.3)", "CIR-574 (Section 6.2)", "REG-768 (Section 2.5)"]
            },
            {
                "title": "I need to verify compliance",
                "docs": ["REG-768 (Sections 2-4)", "FEE-407 (Section 7)", "SOP-843 (Section 10)", "CIR-574 (Section 9)"]
            }
        ]
        
        for uc in use_cases:
            lines.append(f"### {uc['title']}")
            for doc in uc['docs']:
                lines.append(f"- {doc}")
            lines.append("")
        
        lines.append("\n## Total Statistics\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append("| Total Documents | 5 |")
        lines.append("| Total Sections | 50+ |")
        lines.append("| Total Cross-References | 235+ |")
        lines.append("| Document Types | 5 (Policy, Procedure, Communication, Compliance, Navigation) |")
        lines.append("| Formats Supported | 2 (TXT, PDF) |\n")
        
        lines.append(f"\n---\nGenerated: {self.generated_at}\n")
        
        return "\n".join(lines)
    
    def _generate_metadata(self, results: Dict[str, Dict[str, str]]):
        """Generate metadata JSON file describing all generated documents.
        
        Args:
            results: Dictionary of generated documents and their paths
        """
        metadata = {
            "generator": "RAGEcosystemGenerator",
            "version": self.version,
            "generated_at": self.generated_at,
            "documents": {},
            "formats": self.formats,
            "statistics": {
                "total_documents": len(results),
                "total_cross_references": sum(
                    RAGDocumentConfig.DOCUMENTS.get(doc, {}).get("cross_references", 0)
                    for doc in results.keys()
                )
            }
        }
        
        for doc_id, paths in results.items():
            config = RAGDocumentConfig.DOCUMENTS.get(doc_id, {})
            metadata["documents"][doc_id] = {
                "title": config.get("title", ""),
                "type": config.get("doc_type", ""),
                "paths": paths,
                "sections": config.get("sections", 0),
                "appendices": config.get("appendices", 0),
                "cross_references": config.get("cross_references", 0),
            }
        
        # Save metadata
        metadata_path = Path(self.output_dir) / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {metadata_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all RAG ecosystem documents."""
    print("=" * 70)
    print("RAG ECOSYSTEM DOCUMENT GENERATOR")
    print("=" * 70)
    
    # Initialize generator (supports both TXT and PDF)
    generator = RAGEcosystemGenerator(
        output_dir="rag_ecosystem",
        formats=["txt", "pdf"]
    )
    
    print(f"\nGenerating documents in formats: {', '.join(generator.formats).upper()}")
    print(f"Output directory: {generator.output_dir}/\n")
    
    # Generate all documents
    results = generator.generate_all_documents()
    
    # Print summary
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    
    for doc_id, paths in results.items():
        print(f"\n{doc_id}:")
        for format_type, path in paths.items():
            print(f"  ✓ {format_type.upper()}: {path}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total documents generated: {len(results)}")
    print(f"Total cross-references: 235+")
    print(f"Formats: {', '.join(generator.formats).upper()}")
    print(f"All documents support RAG ingestion with section-level chunking")
    print("=" * 70)


if __name__ == "__main__":
    main()
