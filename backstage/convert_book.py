import os
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet


def get_right_format(file):
    base, extension = os.path.splitext(file)
    if extension == ".epub":
        new_file = epub_to_pdf(file)
        print(new_file)
        return new_file
    return file


def _ensure_pdf_path(epub_file: str, other_path: str | None) -> str:
    """
    Decide o caminho final do PDF:
    - None            -> mesmo diretório do EPUB, mesmo nome, .pdf
    - diretório       -> coloca lá o .pdf com o mesmo nome do EPUB
    - ficheiro sem ext-> acrescenta .pdf
    - ficheiro .pdf   -> usa tal como está
    - ficheiro com outra ext -> troca para .pdf
    Cria a pasta de destino se não existir.
    """
    epub_base = os.path.splitext(os.path.basename(epub_file))[0]

    if other_path is None:
        # Mesmo diretório do EPUB
        pdf_path = os.path.join(os.path.dirname(epub_file), epub_base + ".pdf")
    else:
        # Se for um diretório (ou terminar em separador), meter o ficheiro lá dentro
        is_dir_hint = other_path.endswith((os.sep, os.altsep or os.sep))
        if is_dir_hint or os.path.isdir(other_path):
            pdf_path = os.path.join(other_path, epub_base + ".pdf")
        else:
            # other_path parece ser um ficheiro
            root, ext = os.path.splitext(other_path)
            if ext.lower() != ".pdf":
                pdf_path = root + ".pdf"
            else:
                pdf_path = other_path

    # Garante que a pasta existe
    dest_dir = os.path.dirname(pdf_path) or "."
    os.makedirs(dest_dir, exist_ok=True)
    return pdf_path


def epub_to_pdf(epub_file, other_path=None):
    pdf_path = _ensure_pdf_path(epub_file, other_path)

    styles = getSampleStyleSheet()
    book = epub.read_epub(epub_file)
    story = []

    for idref, _ in book.spine:  # ordem correta (spine)
        item = book.get_item_with_id(idref)
        if not item or item.get_type() != ITEM_DOCUMENT:
            continue

        soup = BeautifulSoup(item.get_body_content(), "html.parser")

        # quebra de página entre capítulos
        if story:
            story.append(PageBreak())

        for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            txt = tag.get_text(strip=True)
            if not txt:
                continue
            story.append(Paragraph(txt, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(pdf_path)
    doc.build(story)
    print(f"✔ PDF criado: {pdf_path}")
    return pdf_path
