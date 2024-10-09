from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib

def generate_name_from_link(link:str):
    return link.split('/')[-1].replace('.', '').replace('=', '').replace('?', '').replace('pdf', '.txt')

def text_splitter(text:str, chunck_size:int):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=chunck_size,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.create_documents([text])

    return chunks

def hash_document(document):
    # return hashlib.sha256(document.encode()).hexdigest()
    return hashlib.md5(document.encode()).hexdigest()