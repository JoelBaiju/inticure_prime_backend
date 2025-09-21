import pdfkit
from django.template.loader import render_to_string
from django.conf import settings


class PrescriptionPDFGenerator:
    @staticmethod
    def generate_prescription_pdf(context):
        """Generate prescription PDF from context data"""
        config = PrescriptionPDFGenerator.get_pdf_config()
        html_string = render_to_string('prescription.html', context)
        
        try:
            pdf = pdfkit.from_string(html_string, False, configuration=config)
            return pdf
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    @staticmethod
    def get_pdf_config():
        """Get PDF generation configuration"""
        # TODO: Move this to settings or environment variable
        path_wkhtmltopdf = getattr(
            settings, 
            'WKHTMLTOPDF_PATH' )   
        return pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    @staticmethod
    def validate_pdf_requirements():
        """Validate that required PDF generation tools are available"""
        try:
            config = PrescriptionPDFGenerator.get_pdf_config()
            # Test if wkhtmltopdf is accessible
            return True
        except Exception:
            return False