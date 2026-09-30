import pymupdf


def extract_pages_from_pdf(pdf_file):

    try:

        document = pymupdf.open(
            stream=pdf_file.getvalue(),
            filetype="pdf"
        )

        pages = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            page_text = page.get_text().strip()

            if page_text:

                pages.append({
                    "page": page_number,
                    "text": page_text
                })

        document.close()

        return pages

    except Exception as e:

        raise Exception(
            f"Could not read PDF: {e}"
        )