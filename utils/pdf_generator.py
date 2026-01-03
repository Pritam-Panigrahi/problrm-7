from weasyprint import HTML, CSS
from flask import render_template
import os


def generate_pdf_resume_from_html(user_data, categorized_skills, output_path):
    """
    Generate a PDF resume by rendering HTML template with WeasyPrint.
    This ensures the PDF matches the HTML preview pixel-perfectly.
    
    Args:
        user_data: Dictionary containing user information
        categorized_skills: Dictionary with categorized skills (technical_skills, tools_equipment, soft_skills)
        output_path: Path where the PDF should be saved
    
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Create a user object from the data for template rendering
        class User:
            def __init__(self, data):
                self.name = data.get('name', '')
                self.phone = data.get('phone', '')
                self.trade = data.get('trade', '')
                self.experience_years = data.get('experience_years', 0)
                self.location = data.get('location', '')
                self.skills = data.get('skills', [])
                self.education = data.get('education', '')
                self.certifications = data.get('certifications', '')
                self.work_history = data.get('work_history', [])
                self.resume_complete = data.get('resume_complete', 0)
        
        user = User(user_data)
        
        # Render the HTML template
        html_content = render_template(
            'worker/resume_pdf.html',
            user=user,
            categorized_skills=categorized_skills
        )
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(output_path)
        
        return True
    
    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}")
        return False


# Keep the old function for backward compatibility (deprecated)
def generate_pdf_resume(user_data, resume_content, output_path, template='classic'):
    """
    DEPRECATED: Old ReportLab-based PDF generation.
    Use generate_pdf_resume_from_html() for pixel-perfect HTML-to-PDF conversion.
    
    This function is kept for backward compatibility but should not be used.
    """
    print("Warning: generate_pdf_resume() is deprecated. Use generate_pdf_resume_from_html() instead.")
    
    # Import inside function to avoid loading reportlab if not needed
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.colors import HexColor
    
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.6*inch, bottomMargin=0.6*inch)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Header styles
        name_style = ParagraphStyle(
            'Name',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        )
        
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=16,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=8,
            spaceBefore=14,
            fontName='Helvetica-Bold',
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=14
        )
        
        # Build header
        name = user_data.get('name', 'Resume')
        story.append(Paragraph(name.upper(), name_style))
        
        contact_parts = []
        if user_data.get('phone'):
            contact_parts.append(user_data['phone'])
        if user_data.get('location'):
            contact_parts.append(user_data['location'])
        if user_data.get('trade'):
            contact_parts.append(user_data['trade'])
        
        contact_info = ' | '.join(contact_parts)
        story.append(Paragraph(contact_info, contact_style))
        
        # Add horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#1a1a1a'), 
                               spaceBefore=0, spaceAfter=12))
        
        # Process resume content
        lines = resume_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.08*inch))
                continue
            
            if line.isupper() or line.endswith(':'):
                story.append(Paragraph(line, section_heading_style))
            else:
                if line.startswith('-') or line.startswith('•'):
                    line = '• ' + line.lstrip('-• ')
                story.append(Paragraph(line, body_style))
        
        doc.build(story)
        return True
    
    except Exception as e:
        print(f"Error generating PDF with ReportLab: {e}")
        return False
