from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os

class GoogleSlidesGenerator:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            'credentials/google_service_account.json',
            scopes=['https://www.googleapis.com/auth/presentations',
                   'https://www.googleapis.com/auth/drive']
        )
        self.slides_service = build('slides', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.template_id = os.getenv('GOOGLE_SLIDES_TEMPLATE_ID')

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