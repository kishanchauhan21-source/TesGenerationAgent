from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class DocumentArtifact:
    name: str
    kind: str
    path: Optional[str] = None


@dataclass
class DocumentAnalysis:
    source_path: Path
    file_type: str
    text: str = ""
    requirements: List[str] = field(default_factory=list)
    attachments: List[DocumentArtifact] = field(default_factory=list)
    images: List[DocumentArtifact] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


SUPPORTED_EXTENSIONS = {".doc", ".docx", ".pdf", ".txt"}


def detect_file_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: {sorted(SUPPORTED_EXTENSIONS)}")
    return suffix


def parse_document(file_path: Path) -> DocumentAnalysis:
    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    file_type = detect_file_type(file_path)
    text = ""
    attachments: List[DocumentArtifact] = []
    images: List[DocumentArtifact] = []

    if file_type == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        for page in reader.pages:
            text += page.extract_text() or "\n"
        for name, content in getattr(reader, "attachments", {}).items():
            attachments.append(DocumentArtifact(name=name, kind="attachment", path=str(file_path.parent / name)))
        for page_index, page in enumerate(reader.pages, start=1):
            try:
                for image_index, image in enumerate(page.images, start=1):
                    images.append(DocumentArtifact(name=f"page_{page_index}_image_{image_index}", kind="image", path=image.name))
            except Exception:
                continue

    elif file_type == ".docx":
        import zipfile
        from xml.etree import ElementTree as ET

        with zipfile.ZipFile(file_path) as zf:
            xml_content = zf.read("word/document.xml")
            root = ET.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = root.findall(".//w:t", ns)
            text = "\n".join(node.text or "" for node in paragraphs)

            media_files = [name for name in zf.namelist() if name.startswith("word/media/")]
            for media in media_files:
                if media.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".wmf")):
                    images.append(DocumentArtifact(name=media.split("/")[-1], kind="image", path=media))

            for name in zf.namelist():
                if name.startswith("word/embeddings/") or name.startswith("word/attachments/"):
                    attachments.append(DocumentArtifact(name=name.split("/")[-1], kind="attachment", path=name))

    elif file_type == ".doc":
        import shutil
        import subprocess

        antiword = shutil.which("antiword")
        soffice = shutil.which("soffice")
        if antiword:
            result = subprocess.run([antiword, str(file_path)], capture_output=True, text=True, check=False)
            text = result.stdout or ""
        elif soffice:
            temp_path = file_path.with_suffix(".txt")
            subprocess.run([soffice, "--headless", "--convert-to", "txt", str(file_path), "--outdir", str(file_path.parent)], check=False)
            if temp_path.exists():
                text = temp_path.read_text(encoding="utf-8", errors="ignore")
        else:
            raise EnvironmentError(".doc extraction requires antiword or libreoffice to be installed.")

    elif file_type == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")

    requirements = extract_requirements(text)
    attached_files = list_attachments_nearby(file_path)
    attachments.extend(attached_files)

    return DocumentAnalysis(
        source_path=file_path,
        file_type=file_type,
        text=text,
        requirements=requirements,
        attachments=attachments,
        images=images,
        metadata={"source_name": file_path.name, "parent_dir": str(file_path.parent)},
    )


def extract_requirements(text: str) -> list[str]:
    import re

    candidates = re.findall(r"(?:Req(?:uisement)?(?:\s*No\.?|\s*#)?\s*[:#-]?\s*|Requirement\s*[:#-]?\s*)([A-Z0-9.-]+)", text, flags=re.IGNORECASE)
    if candidates:
        return [item.strip() for item in candidates]

    fallback = []
    for line in text.splitlines():
        if re.search(r"\b(requirement|req|business rule|functional|feature)\b", line, flags=re.IGNORECASE):
            fallback.append(line.strip())
    return fallback[:20]


def list_attachments_nearby(file_path: Path) -> list[DocumentArtifact]:
    artifacts: list[DocumentArtifact] = []
    if not file_path.parent.exists():
        return artifacts

    for child in file_path.parent.iterdir():
        if child.is_file() and child.name.lower() not in {file_path.name.lower()}:
            if child.suffix.lower() in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg", ".bmp"}:
                artifacts.append(DocumentArtifact(name=child.name, kind="attachment", path=str(child)))
    return artifacts
