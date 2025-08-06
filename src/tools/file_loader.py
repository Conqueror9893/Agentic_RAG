import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from langchain.schema import Document

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredFileLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredXMLLoader,
    OutlookMessageLoader,
    UnstructuredEmailLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Primary loader mapping
PRIMARY_LOADER_MAPPING = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".doc": UnstructuredFileLoader,
    ".docm": UnstructuredFileLoader,
    ".odt": UnstructuredFileLoader,
    ".rtf": UnstructuredFileLoader,
    ".txt": TextLoader,
    ".log": TextLoader,
    ".htm": UnstructuredHTMLLoader,
    ".html": UnstructuredHTMLLoader,
    ".md": UnstructuredMarkdownLoader,
    ".xml": UnstructuredXMLLoader,
    ".msg": OutlookMessageLoader,
    ".eml": UnstructuredEmailLoader,
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp"}
PDF_EXTS = {".pdf"}

# PaddleOCR model (lazy init)
OCR_MODEL = PaddleOCR(use_angle_cls=True, lang="en")  # downloads models on first run

# Heuristic: if a document's text is shorter than this, consider it sparse and try OCR
SPARSE_LENGTH_THRESHOLD = 100  # characters


def is_tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def convert_with_libreoffice(src_path: str, target_ext: str) -> str:
    if not is_tool_available("soffice"):
        raise RuntimeError("LibreOffice CLI (soffice) not found in PATH.")
    with tempfile.TemporaryDirectory() as td:
        cmd = [
            "soffice",
            "--headless",
            "--convert-to",
            target_ext,
            "--outdir",
            td,
            src_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        basename = Path(src_path).stem
        converted = Path(td) / f"{basename}.{target_ext}"
        if not converted.exists():
            raise RuntimeError(f"LibreOffice conversion failed for {src_path} to .{target_ext}")
        dest = tempfile.mktemp(suffix=f".{target_ext}")
        shutil.copy(converted, dest)
        return dest


def ocr_image_file(path: str):
    result = OCR_MODEL.ocr(path, cls=True)
    lines = []
    for block in result:
        for line in block:
            text = line[1][0]
            lines.append(text)
    combined_text = "\n".join(lines)
    return Document(
        page_content=combined_text,
        metadata={"source": path, "fallback": "paddleocr_image"},
    )


def ocr_scanned_pdf(path: str):
    docs = []
    try:
        images = convert_from_path(path)
    except Exception as e:
        raise RuntimeError(f"PDF to image conversion failed: {e}")

    for i, pil_image in enumerate(images):
        img_array = np.array(pil_image)
        result = OCR_MODEL.ocr(img_array, cls=True)
        lines = []
        for block in result:
            for line in block:
                lines.append(line[1][0])
        page_text = "\n".join(lines)
        metadata = {
            "source": path,
            "page": i + 1,
            "fallback": "paddleocr_pdf",
        }
        docs.append(Document(page_content=page_text, metadata=metadata))
    return docs


def try_loader(loader_cls, path):
    try:
        loader = loader_cls(path)
        loaded = loader.load()
        # Normalize to LangChain Document if not already
        results = []
        for d in loaded:
            if isinstance(d, Document):
                results.append(d)
            else:
                results.append(Document(page_content=getattr(d, "page_content", str(d)),
                                        metadata=getattr(d, "metadata", {"source": path})))
        return results
    except Exception as e:
        raise RuntimeError(f"{loader_cls.__name__} failed: {e}")


def load_with_fallback(file_path: str):
    ext = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    tried = []
    # 1. Primary loader
    if ext in PRIMARY_LOADER_MAPPING:
        loader_cls = PRIMARY_LOADER_MAPPING[ext]
        try:
            docs = try_loader(loader_cls, file_path)
            # if content sparse, maybe it's a scanned PDF/image
            docs = maybe_augment_with_ocr_if_sparse(file_path, docs, ext)
            return docs
        except Exception as e:
            tried.append((loader_cls.__name__, str(e)))

    # 2. Fallback conversions
    if ext in {".doc", ".docm", ".odt"}:
        try:
            converted = convert_with_libreoffice(file_path, "docx")
            docs = try_loader(Docx2txtLoader, converted)
            return docs
        except Exception as e:
            tried.append(("libreoffice->docx", str(e)))

    if ext in {".mht", ".mhtml"}:
        try:
            converted = convert_with_libreoffice(file_path, "html")
            docs = try_loader(UnstructuredHTMLLoader, converted)
            return docs
        except Exception as e:
            tried.append(("libreoffice->html", str(e)))

    if ext == ".rtf":
        if is_tool_available("pandoc"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as out:
                    subprocess.run(
                        ["pandoc", file_path, "-t", "plain", "-o", out.name],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    docs = try_loader(TextLoader, out.name)
                    return docs
            except Exception as e:
                tried.append(("pandoc->txt", str(e)))
        else:
            tried.append(("pandoc missing", "pandoc not installed"))

    # 3. OCR fallbacks for images and scanned PDFs
    if ext in IMAGE_EXTS:
        try:
            return [ocr_image_file(file_path)]
        except Exception as e:
            tried.append(("paddleocr_image", str(e)))

    if ext in PDF_EXTS:
        try:
            ocr_docs = ocr_scanned_pdf(file_path)
            if ocr_docs:
                return ocr_docs
        except Exception as e:
            tried.append(("paddleocr_pdf", str(e)))

    # 4. Last resort: plain text loader
    try:
        docs = try_loader(TextLoader, file_path)
        return docs
    except Exception as e:
        tried.append(("TextLoader", str(e)))

    summary = "; ".join(f"{n}: {m}" for n, m in tried)
    raise RuntimeError(f"All loading attempts failed for {file_path}. Details: {summary}")


def maybe_augment_with_ocr_if_sparse(file_path: str, docs: list[Document], ext: str):
    """
    If the loaded documents are too short / sparse and input is image/pdf, fallback to OCR.
    """
    combined_len = sum(len(d.page_content.strip()) for d in docs)
    if combined_len >= SPARSE_LENGTH_THRESHOLD:
        return docs  # sufficient content
    # if PDF or image, try OCR augmentation
    if ext in IMAGE_EXTS:
        try:
            ocr_doc = ocr_image_file(file_path)
            return [ocr_doc]
        except Exception:
            return docs  # keep original even if sparse
    if ext == ".pdf":
        try:
            ocr_docs = ocr_scanned_pdf(file_path)
            return ocr_docs if ocr_docs else docs
        except Exception:
            return docs
    return docs


def load_documents(directory_path: str = "./data"):
    print(f"Loading documents from {directory_path}...")
    documents = []

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else None

        if not ext:
            print(f"Skipping {filename}: no extension detected")
            continue

        try:
            docs = load_with_fallback(file_path)
            documents.extend(docs)
            print(f"Successfully loaded {filename}")
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

    if not documents:
        print("No documents were loaded.")
        return []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_documents = text_splitter.split_documents(documents)

    print(f"Loaded and split {len(documents)} documents into {len(chunked_documents)} chunks.")
    return chunked_documents


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.makedirs("./data")
    with open("./data/sample.txt", "w") as f:
        f.write("This is a sample text file. It contains information about the RAG system.")

    docs = load_documents()
    if docs:
        print(f"\nSuccessfully loaded {len(docs)} chunks.")
        print("\nFirst chunk of the first document:")
        print(docs[0].page_content)
        print("\nMetadata of the first chunk:")
        print(docs[0].metadata)
    else:
        print("\nNo documents were loaded. Please check the data directory and file formats.")
