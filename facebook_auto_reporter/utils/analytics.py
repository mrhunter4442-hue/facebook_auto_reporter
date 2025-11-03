import json
import csv
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class AnalyticsEngine:
    def __init__(self):
        self.reports_folder = "./data/reports/"
        os.makedirs(self.reports_folder, exist_ok=True)
        
    def generate_comprehensive_report(self, reporting_data):
        """Comprehensive analytics report generate করুন"""
        try:
            # Generate multiple report formats
            self.generate_json_report(reporting_data)
            self.generate_csv_report(reporting_data)
            self.generate_excel_report(reporting_data)
            self.generate_pdf_report(reporting_data)
            
            print(f"Analytics reports generated in: {self.reports_folder}")
            
        except Exception as e:
            print(f"Analytics report generation failed: {e}")
    
    def generate_json_report(self, data):
        """JSON report generate করুন"""
        filename = f"{self.reports_folder}report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_reports': len(data),
            'successful_reports': len([r for r in data if r.get('report_success')]),
            'violation_stats': self.get_violation_statistics(data),
            'detailed_data': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def generate_csv_report(self, data):
        """CSV report generate করুন"""
        filename = f"{self.reports_folder}report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Target URL', 'Violation Type', 'Confidence Score', 
                'Report Success', 'Timestamp', 'Evidence'
            ])
            
            # Write data
            for item in data:
                writer.writerow([
                    item.get('target_url', ''),
                    item.get('violation', {}).get('violation_type', ''),
                    item.get('violation', {}).get('confidence_score', ''),
                    item.get('report_success', ''),
                    item.get('timestamp', ''),
                    item.get('violation', {}).get('evidence', '')[:100]  # First 100 chars
                ])
    
    def generate_excel_report(self, data):
        """Excel report generate করুন"""
        try:
            filename = f"{self.reports_folder}report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Create DataFrame
            df_data = []
            for item in data:
                df_data.append({
                    'Target URL': item.get('target_url', ''),
                    'Violation Type': item.get('violation', {}).get('violation_type', ''),
                    'Confidence Score': item.get('violation', {}).get('confidence_score', ''),
                    'Report Success': 'Yes' if item.get('report_success') else 'No',
                    'Timestamp': item.get('timestamp', ''),
                    'Evidence': item.get('violation', {}).get('evidence', ''),
                    'Report Category': item.get('violation', {}).get('report_category', '')
                })
            
            df = pd.DataFrame(df_data)
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Report Data', index=False)
                
                # Add summary sheet
                summary_data = self.get_summary_data(data)
                summary_df = pd.DataFrame([summary_data])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
        except Exception as e:
            print(f"Excel report generation failed: {e}")
    
    def generate_pdf_report(self, data):
        """PDF report generate করুন"""
        try:
            filename = f"{self.reports_folder}report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("Facebook Auto Reporter - Analytics Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Summary
            summary_data = self.get_summary_data(data)
            summary_text = f"""
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Total Reports: {summary_data['total_reports']}
            Successful Reports: {summary_data['successful_reports']}
            Success Rate: {summary_data['success_rate']}%
            """
            
            summary = Paragraph(summary_text, styles['Normal'])
            elements.append(summary)
            elements.append(Spacer(1, 12))
            
            # Violation statistics table
            violation_stats = self.get_violation_statistics(data)
            table_data = [['Violation Type', 'Count']]
            
            for violation_type, count in violation_stats.items():
                table_data.append([violation_type, str(count)])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
            
        except Exception as e:
            print(f"PDF report generation failed: {e}")
    
    def get_summary_data(self, data):
        """Summary data calculate করুন"""
        total = len(data)
        successful = len([r for r in data if r.get('report_success')])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            'total_reports': total,
            'successful_reports': successful,
            'success_rate': round(success_rate, 2)
        }
    
    def get_violation_statistics(self, data):
        """Violation statistics calculate করুন"""
        stats = {}
        
        for item in data:
            violation_type = item.get('violation', {}).get('violation_type', 'Unknown')
            stats[violation_type] = stats.get(violation_type, 0) + 1
        
        return stats