import fitz  # PyMuPDF
import re
import docx
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

def extract_text_and_links(file):
    text = ""
    links = []

    if file.name.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
            links += [l["uri"] for l in page.get_links() if "uri" in l]

    elif file.name.endswith('.docx'):
        file.seek(0)
        text, links = extract_docx_text_and_hyperlinks(file)

    return text, list(set(links))

def extract_docx_text_and_hyperlinks(docx_file):
    text = ""
    links = []

    document = docx.Document(docx_file)
    for para in document.paragraphs:
        text += para.text + "\n"
        links += re.findall(r'(https?://\S+)', para.text)

    docx_file.seek(0)
    zipf = zipfile.ZipFile(BytesIO(docx_file.read()))
    rels_path = "word/_rels/document.xml.rels"

    link_map = {}
    if rels_path in zipf.namelist():
        rels_root = ET.fromstring(zipf.read(rels_path))
        for rel in rels_root:
            r_id = rel.attrib.get('Id')
            target = rel.attrib.get('Target')
            if r_id and target and target.startswith("http"):
                link_map[r_id] = target

    document_xml = ET.fromstring(zipf.read("word/document.xml"))
    for elem in document_xml.iter():
        if elem.tag.endswith("hyperlink"):
            r_id = elem.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            if r_id in link_map:
                links.append(link_map[r_id])

    return text, list(set(links))
