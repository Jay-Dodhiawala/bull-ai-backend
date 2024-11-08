from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import markdown
from bs4 import BeautifulSoup
from supabase import create_client, Client
import base64
import uuid

class GoogleSlidesGenerator:
    def __init__(self):
        # Create credentials dict from env variables
        credentials_dict = {
            "type": "service_account",
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),  # Important: replace \\n with \n
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": "googleapis.com"
        }
        
        # Create credentials object from dict
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/presentations',
                   'https://www.googleapis.com/auth/drive']
        )
        self.slides_service = build('slides', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.template_id = os.getenv('GOOGLE_SLIDES_TEMPLATE_ID')
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def _clean_markdown(self, text):
        """Convert markdown to plain text while preserving structure"""
        # Convert markdown to HTML
        html = markdown.markdown(text)
        
        # Convert HTML to plain text while preserving bullets
        soup = BeautifulSoup(html, 'html.parser')
        
        # Replace <li> with bullet points and preserve template formatting
        for li in soup.find_all('li'):
            li.replace_with('• ' + li.get_text())
        
        # Get text and clean up excessive newlines while preserving template format
        text = soup.get_text()
        # Remove multiple newlines while preserving single ones
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Ensure text matches template placeholder format
        text = text.strip()
        
        return text

    def create_report(self, data):
        """Create a new presentation from template and replace variables"""
        try:
            # Copy template
            copy_title = f"{data['company_name']} Analysis Report"
            copied_file = self.drive_service.files().copy(
                fileId=self.template_id,
                body={'name': copy_title}
            ).execute()
            
            presentation_id = copied_file['id']

            # Prepare requests to replace text
            requests = []
            for key, value in data.items():
                if isinstance(value, str):
                    value = self._clean_markdown(value)
                
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': f'{{{{{key}}}}}',
                            'matchCase': True
                        },
                        'replaceText': str(value)
                    }
                })

            # Execute the requests
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()

            # Export as PDF
            response = self.drive_service.files().export(
                fileId=presentation_id,
                mimeType='application/pdf'
            ).execute()

            # Cleanup - Delete the presentation after exporting
            self.drive_service.files().delete(fileId=presentation_id).execute()
            print (response)
            return response

        except Exception as e:
            print(f"Error creating report: {str(e)}")
            raise

    def store_pdf_link(self, pdf_data: bytes) -> str:
        """Store PDF in Supabase Storage bucket and database"""
        try:
            # Generate unique filename
            filename = f"report_{uuid.uuid4()}.pdf"
            
            # Upload the PDF file to the storage bucket
            self.supabase.storage.from_('generated_pdf').upload(
                path=filename,
                file=pdf_data,
                file_options={"content-type": "application/pdf"}
            )
            
            # Get CDN URL instead of direct storage URL
            public_url = f"https://{os.getenv('SUPABASE_PROJECT_ID')}.supabase.co/storage/v1/object/public/generated_pdf/{filename}"
            
            # Store in database
            self.supabase.table('generated_pdf').insert({
                'link': public_url,
                'file_data': base64.b64encode(pdf_data).decode('utf-8')
            }).execute()
            
            return public_url
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            raise