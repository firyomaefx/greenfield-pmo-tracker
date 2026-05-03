"""
Greenfield Factory Project Tracker - PDF Export Module
Generates PMP-grade PDF reports from project data.
"""

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
import requests
from io import BytesIO


class PDFReportGenerator:
    """Generate professional PDF reports for Greenfield projects."""
    
    def __init__(self, filename="Greenfield_Report.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        self.styles = self._setup_styles()
        self.story = []
        
    def _setup_styles(self):
        """Setup custom paragraph styles."""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2ecc71'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2ecc71'),
            borderPadding=5,
            leftIndent=0
        ))
        
        # Metric style
        styles.add(ParagraphStyle(
            name='Metric',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333'),
            spaceAfter=5
        ))
        
        # Status styles
        styles.add(ParagraphStyle(
            name='StatusCompleted',
            parent=styles['Normal'],
            textColor=colors.HexColor('#2ecc71'),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='StatusPlanned',
            parent=styles['Normal'],
            textColor=colors.HexColor('#f39c12'),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='StatusDelayed',
            parent=styles['Normal'],
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def _create_header(self, title, subtitle=""):
        """Create report header."""
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        
        if subtitle:
            self.story.append(Paragraph(
                f"<i>{subtitle}</i>",
                ParagraphStyle(name='Subtitle', parent=self.styles['Normal'], 
                             alignment=TA_CENTER, textColor=colors.grey, fontSize=10)
            ))
        
        self.story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | PMP Professional Dashboard",
            ParagraphStyle(name='DateStamp', parent=self.styles['Normal'],
                         alignment=TA_CENTER, textColor=colors.grey, fontSize=8)
        ))
        self.story.append(Spacer(1, 20))
    
    def _add_executive_summary(self, projects):
        """Add executive summary section."""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Calculate metrics
        total_projects = len(projects)
        kulim_count = len([p for p in projects if p.get('location') == 'Kulim'])
        batu_count = len([p for p in projects if p.get('location') == 'Batu Kawan'])
        
        total_investment = self._extract_total_investment(projects)
        total_jobs = sum(p.get('jobs_estimate', 0) for p in projects)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Active Projects', str(total_projects)],
            ['Kulim Sites', str(kulim_count)],
            ['Batu Kawan Sites', str(batu_count)],
            ['Total Estimated Investment', f"~RM {total_investment / 1e9:.1f}B+"],
            ['Total Estimated Jobs', f"{total_jobs:,}"],
            ['Reporting Date', datetime.now().strftime('%Y-%m-%d')]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8f4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f8f4'), colors.white])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def _extract_total_investment(self, projects):
        """Extract total investment from projects."""
        import re
        total = 0
        for p in projects:
            inv_range = p.get('investment_range', '').upper()
            if 'B' in inv_range and 'RM' in inv_range:
                # Extract number before B
                import re
                match = re.search(r'RM\s*([0-9.]+)\s*B', inv_range)
                if match:
                    total += float(match.group(1)) * 1e9
            elif 'M' in inv_range and 'RM' in inv_range:
                match = re.search(r'RM\s*([0-9.]+)\s*M', inv_range)
                if match:
                    total += float(match.group(1)) * 1e6
        return total
    
    def _add_project_details(self, projects, location_filter=None):
        """Add detailed project cards."""
        filtered = projects
        if location_filter:
            filtered = [p for p in projects if p.get('location') in location_filter]
        
        self.story.append(Paragraph(f"Project Details ({len(filtered)} Projects)", self.styles['SectionHeader']))
        
        for project in filtered:
            # Project header
            loc_color = '#2ecc71' if project.get('location') == 'Kulim' else '#3498db'
            header_text = f"""
            <b>{project.get('company', 'N/A')}</b> 
            <span color="{loc_color}">[{project.get('location', 'N/A')}]</span>
            """
            self.story.append(Paragraph(header_text, self.styles['Heading3']))
            
            # Meta info
            meta_text = f"""
            <b>Sector:</b> {project.get('sector', 'N/A')} | 
            <b>Phase:</b> {project.get('phase', 'N/A')} | 
            <b>Investment:</b> {project.get('investment_range', 'TBD')} | 
            <b>Est. Jobs:</b> {project.get('jobs_estimate', 'N/A')}
            """
            self.story.append(Paragraph(meta_text, self.styles['Metric']))
            
            # Latest news
            if project.get('latest'):
                news_para = Paragraph(
                    f"? <b>Latest:</b> {project['latest']}",
                    ParagraphStyle(name='NewsBox', parent=self.styles['Normal'],
                                 backColor=colors.HexColor('#fffdf5'),
                                 borderWidth=1, borderColor=colors.HexColor('#f39c12'),
                                 borderPadding=8, fontSize=9)
                )
                self.story.append(news_para)
                self.story.append(Spacer(1, 5))
            
            # Milestones table
            milestones = project.get('milestones', [])
            if milestones:
                table_data = [['Milestone', 'Target', 'Actual', 'Status']]
                for m in milestones:
                    status_style = 'StatusCompleted' if m.get('status') == 'Completed' else 'StatusPlanned'
                    table_data.append([
                        m.get('milestone', ''),
                        m.get('target', ''),
                        m.get('actual', ''),
                        m.get('status', '')
                    ])
                
                t = Table(table_data, colWidths=[2.8*inch, 1.2*inch, 1.2*inch, 1*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                ]))
                self.story.append(t)
            
            self.story.append(Spacer(1, 15))
    
    def _add_risk_register(self, risks):
        """Add PMP-style risk register."""
        self.story.append(Paragraph("Risk Register", self.styles['SectionHeader']))
        
        risk_data = [['Risk ID', 'Description', 'Impact', 'Mitigation', 'Owner']]
        for risk in risks:
            risk_data.append([
                risk.get('Risk ID', ''),
                risk.get('Description', ''),
                risk.get('Impact', ''),
                risk.get('Mitigation', ''),
                risk.get('Owner', '')
            ])
        
        t = Table(risk_data, colWidths=[0.6*inch, 1.8*inch, 0.8*inch, 2*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef9f9')])
        ]))
        
        self.story.append(t)
        self.story.append(Spacer(1, 20))
    
    def _add_footer(self):
        """Add report footer."""
        self.story.append(Spacer(1, 30))
        self.story.append(Paragraph(
            "???????????????????????????????????????????????????",
            ParagraphStyle(name='Divider', alignment=TA_CENTER, textColor=colors.grey)
        ))
        self.story.append(Paragraph(
            f"<i>Greenfield PMO Tracker v2.2 | PMP Professional Dashboard | {datetime.now().strftime('%Y')}</i>",
            ParagraphStyle(name='Footer', parent=self.styles['Normal'],
                         alignment=TA_CENTER, textColor=colors.grey, fontSize=8)
        ))
        self.story.append(Paragraph(
            "<i>Confidential - For Internal Use Only</i>",
            ParagraphStyle(name='Confidential', alignment=TA_CENTER, 
                         textColor=colors.grey, fontSize=7)
        ))
    
    def generate_full_report(self, projects, risks, include_charts=True):
        """Generate complete PDF report."""
        print("[DOC] Generating PDF report...")
        
        self._create_header(
            "[FACTORY] Greenfield Factory Project Dashboard",
            "Kulim & Batu Kawan Mega Projects | Portfolio Status Report"
        )
        
        self._add_executive_summary(projects)
        self._add_project_details(projects)
        self._add_risk_register(risks)
        self._add_footer()
        
        try:
            self.doc.build(self.story)
            print(f"[OK] PDF report generated: {os.path.abspath(self.filename)}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to generate PDF: {str(e)}")
            return False
    
    def generate_filtered_report(self, projects, risks, location_filter, company_filter):
        """Generate filtered PDF report."""
        filtered_projects = [p for p in projects 
                           if p.get('location') in location_filter 
                           and p.get('company') in company_filter]
        
        loc_text = " & ".join(location_filter)
        self._create_header(
            f"[FACTORY] {loc_text} Projects Report",
            f"Filtered View: {len(filtered_projects)} Selected Projects"
        )
        
        if filtered_projects:
            self._add_executive_summary(filtered_projects)
            self._add_project_details(filtered_projects)
            self._add_risk_register(risks)
            
        self._add_footer()
        
        try:
            self.doc.build(self.story)
            print(f"[OK] Filtered PDF generated: {os.path.abspath(self.filename)}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to generate PDF: {str(e)}")
            return False


def generate_pdf_from_html(input_html="dashboard.html", output_pdf="dashboard.pdf"):
    """Convert HTML dashboard to PDF (requires additional tools)."""
    print("? HTML to PDF conversion...")
    
    # Option 1: Use weasyprint if installed
    try:
        import weasyprint
        weasyprint.HTML(input_html).write_pdf(output_pdf)
        print(f"[OK] PDF generated: {output_pdf}")
        return True
    except ImportError:
        pass
    
    # Option 2: Use pdfkit with wkhtmltopdf
    try:
        import pdfkit
        pdfkit.from_file(input_html, output_pdf)
        print(f"[OK] PDF generated: {output_pdf}")
        return True
    except ImportError:
        pass
    
    print("[WARN]? Install weasyprint or pdfkit for HTML-to-PDF conversion:")
    print("   pip install weasyprint")
    print("   OR")
    print("   pip install pdfkit")
    return False


if __name__ == "__main__":
    print("[FACTORY] Greenfield Factory Project PDF Export")
    print("=" * 50)
    
    # Import project data from dashboard
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from dashboard import get_default_projects
        projects = get_default_projects()
        
        # Sample risk data
        risks = [
            {"Risk ID": "R001", "Description": "Supply chain delays", "Impact": "High", "Mitigation": "Dual sourcing strategy", "Owner": "Project Lead"},
            {"Risk ID": "R002", "Description": "Regulatory changes", "Impact": "Medium", "Mitigation": "Government liaison", "Owner": "Compliance Officer"},
            {"Risk ID": "R003", "Description": "Labor shortage", "Impact": "High", "Mitigation": "Local training programs", "Owner": "HR Manager"},
            {"Risk ID": "R004", "Description": "Funding/CAPEX fluctuation", "Impact": "High", "Mitigation": "Phased investment approach", "Owner": "Finance Controller"},
            {"Risk ID": "R005", "Description": "Multiple concurrent site works (KHTP / BKIP)", "Impact": "High", "Mitigation": "Traffic & logistics coordination", "Owner": "PMO Lead"},
            {"Risk ID": "R006", "Description": "Currency/EUR-RM volatility (AIXTRON)", "Impact": "Medium", "Mitigation": "FX hedging", "Owner": "Finance Controller"}
        ]
        
        # Generate full report
        generator = PDFReportGenerator("Greenfield_Full_Report.pdf")
        generator.generate_full_report(projects, risks)
        
        # Generate Kulim-only report
        generator2 = PDFReportGenerator("Greenfield_Kulim_Report.pdf")
        generator2.generate_filtered_report(projects, risks, ["Kulim"], [p['company'] for p in projects if p.get('location') == 'Kulim'])
        
        # Generate Batu Kawan-only report
        generator3 = PDFReportGenerator("Greenfield_BatuKawan_Report.pdf")
        generator3.generate_filtered_report(projects, risks, ["Batu Kawan"], [p['company'] for p in projects if p.get('location') == 'Batu Kawan'])
        
        print("\n[STATS] Generated Reports:")
        print("   ? Greenfield_Full_Report.pdf (All projects)")
        print("   ? Greenfield_Kulim_Report.pdf (Kulim only)")
        print("   ? Greenfield_BatuKawan_Report.pdf (Batu Kawan only)")
        
    except ImportError:
        print("[FAIL] Could not import project data. Make sure dashboard.py exists.")
