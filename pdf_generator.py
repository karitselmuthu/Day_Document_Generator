"""PDF generator for RAG ecosystem documents."""
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors


class RAGPDFGenerator:
    """Generates formatted PDF documents for RAG ecosystem."""
    
    def __init__(self, filename: str, title: str, doc_type: str, version: str = "1.0.0"):
        """Initialize PDF generator.
        
        Args:
            filename: Output PDF filename
            title: Document title
            doc_type: Type of document (FEE-407, SOP-843, etc.)
            version: Document version
        """
        self.filename = filename
        self.title = title
        self.doc_type = doc_type
        self.version = version
        self.created_at = datetime.now().isoformat()
        
    def generate(self, sections: List[Dict[str, str]]) -> str:
        """Generate PDF from sections.
        
        Args:
            sections: List of section dicts with 'title' and 'content' keys
            
        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build story elements
        story = []
        styles = getSampleStyleSheet()
        
        # Add title page
        story.extend(self._create_title_page(styles))
        story.append(PageBreak())
        
        # Add sections
        for section in sections:
            story.append(Paragraph(section['title'], styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(section['content'], styles['BodyText']))
            story.append(Spacer(1, 0.3*inch))
        
        # Add footer
        story.append(PageBreak())
        story.extend(self._create_footer(styles))
        
        # Build PDF
        doc.build(story)
        return self.filename
    
    def _create_title_page(self, styles) -> List:
        """Create title page elements."""
        elements = []
        elements.append(Spacer(1, 1.5*inch))
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1,  # CENTER
        )
        elements.append(Paragraph(self.title, title_style))
        
        # Metadata
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.grey,
            spaceAfter=12,
            alignment=1,  # CENTER
        )
        
        elements.append(Paragraph(f"<b>Document Type:</b> {self.doc_type}", meta_style))
        elements.append(Paragraph(f"<b>Version:</b> {self.version}", meta_style))
        elements.append(Paragraph(f"<b>Generated:</b> {self.created_at}", meta_style))
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_footer(self, styles) -> List:
        """Create footer with TOC and metadata."""
        elements = []
        elements.append(Paragraph("<b>Document Information</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        footer_text = f"""
        <b>Document Type:</b> {self.doc_type}<br/>
        <b>Version:</b> {self.version}<br/>
        <b>Generated:</b> {self.created_at}<br/>
        <b>Format:</b> PDF<br/>
        <b>Purpose:</b> RAG Ecosystem Document - Do not distribute without approval
        """
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        return elements


def generate_pdf_from_text(
    filename: str,
    title: str,
    content: str,
    doc_type: str,
    version: str = "1.0.0"
) -> str:
    """Quick function to generate PDF from plain text.
    
    Args:
        filename: Output PDF filename
        title: Document title
        content: Document content (plain text)
        doc_type: Document type identifier
        version: Document version
        
    Returns:
        Path to generated PDF file
    """
    # Split content into sections
    sections = []
    current_section = None
    
    for line in content.split('\n'):
        if line.startswith('##'):
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': line.replace('##', '').strip(),
                'content': ''
            }
        elif current_section:
            current_section['content'] += line + '<br/>'
    
    if current_section:
        sections.append(current_section)
    
    # Generate PDF
    generator = RAGPDFGenerator(filename, title, doc_type, version)
    return generator.generate(sections)


if __name__ == "__main__":
    # Example usage
    sample_content = """
    ## Introduction
    This is the introduction section.
    
    ## Section 1
    Content for section 1.
    
    ## Section 2
    Content for section 2.
    """
    
    pdf_path = generate_pdf_from_text(
        "sample.pdf",
        "Sample Document",
        sample_content,
        "SAMPLE-001",
        "1.0.0"
    )
    print(f"Generated PDF: {pdf_path}")
