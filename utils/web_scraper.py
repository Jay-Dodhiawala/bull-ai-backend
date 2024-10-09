import time
import requests
from bs4 import BeautifulSoup

import io
import os
from pdfminer.high_level import extract_text
from .my_tools import generate_name_from_link, text_splitter


def scrape_links(ticker:str, debug=False):

    start_time = time.time()

    # using requests to send GET request to the page
    response = requests.get(f"https://www.screener.in/company/{ticker}/")
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    pdf_links = {}

    # Define the specific class combinations you're interested in
    class_combinations = [
        'documents flex-column',
        'documents annual-reports flex-column',
        'documents credit-ratings flex-column',
        'documents concalls flex-column'
    ]

    try:

        document_section = soup.find('section', {'id': 'documents'})  # Adjust the selector if needed

        for class_combination in class_combinations:

            if document_section:
                # Find the first link within this section
                link = document_section.find('div', {'class': class_combination})
                # print(link)

                if class_combination == 'documents concalls flex-column':
                    list_item = link.find_all('li')
                    li = list_item[0]
                    
                    # Initialize placeholders for Transcript and PPT links
                    transcript_link = None
                    ppt_link = None

                    # Find "Transcript" and "PPT" links
                    transcript_element = li.find('a', string=lambda text: 'Transcript' in text)  # Finds link with 'Transcript'
                    ppt_element = li.find('a', string=lambda text: 'PPT' in text)  # Finds link with 'PPT'

                    # If a Transcript link is found, get its href
                    if transcript_element:
                        transcript_link = transcript_element.get('href')
                        pdf_links[class_combination+" transcript"] = transcript_link
                        # print(transcript_link)
                    
                    # If a PPT link is found, get its href
                    if ppt_element:
                        ppt_link = ppt_element.get('href')
                        pdf_links[class_combination+" ppt"] = ppt_link
                        # print(ppt_link)

                elif link:
                    href = link.find('a').get('href')
                    # Check if the link is a PDF
                    pdf_links[class_combination] = href
                    # print(href)
                else:
                    pdf_links[class_combination] = 'No links found'
            else:
                pdf_links[class_combination] = 'Document section not found'
    except Exception as e:
        print(f"Error extracting links: {str(e)}")

   

    end_time = time.time()

    if debug:

        # Print the PDF links and time taken
        print(f'PDF links: {pdf_links}')
        print(f'Number of class combinations checked: {len(class_combinations)}')
        print(f'Time taken: {end_time - start_time:.2f} seconds')

    # convert dictionary to list which only contains the links
    pdf_links = [(key, value) for key, value in pdf_links.items()]

    return pdf_links


def scarpe_doc_and_split(link:str, ticker:str, chunk_size:int, save_output:bool, debug=False):
    start_time = time.time()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
        
    session = requests.Session()

    try:
        raw_text_chunks = []

        response = session.get(link, headers=headers, allow_redirects=True)
        
        if response.status_code == 200:
            if link.endswith('.pdf'):
                pdf_content = io.BytesIO(response.content)
                raw_text = extract_text(pdf_content)  
            else:
                #raw_text = response.text
                soup = BeautifulSoup(response.content, 'html.parser')

                # Step 3: Select only the <body> tag content
                body = soup.body

                # Step 4: Remove all script and style elements within the body
                for script_or_style in body(['script', 'style']):
                    script_or_style.decompose()

                # Step 5: Extract the visible text from the body
                body_text = body.get_text(separator=' ')

                # Step 6: Clean up the text by stripping extra whitespace
                raw_text = ' '.join(body_text.split())
                
                if debug:
                    # Print the extracted clean text
                    print(raw_text)

            raw_text_chunks = text_splitter(raw_text, chunk_size|20000)

            filename = generate_name_from_link(link) 


            if save_output:
                # Ensure the directory exists
                if not os.path.exists('data/'):
                    os.makedirs('data/')

                # filename = generate_name_from_link(link) 
                filepath = f'data/{ticker}_{filename}'     

                try:
                    # If the text contains special characters, use UTF-8 to save it
                    with open(filepath, 'w', encoding='utf-8', errors='ignore') as txt_file:
                        txt_file.write(raw_text)
                    if debug:
                        print(f"Text saved to {filename}")
                    
                    # print(f"Extracted text: {raw_text[:1000]}")
                except Exception as e:
                    print(f"Error saving text: {str(e)}")
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error extracting text: {str(e)}")

    end_time = time.time()

    time_taken = end_time - start_time

    if debug:
        print(f'Time taken: {time_taken:.2f} seconds')

    # return f"{ticker}_{filename}" + raw_text + "\n\n"
    return raw_text_chunks 