import hashlib


def create_document_id(file_bytes):

    return hashlib.sha256(
        file_bytes
    ).hexdigest()