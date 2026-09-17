"""
Document Parser Service (§8-9) - CV ingestion pipeline.
Handles PDF and DOCX parsing with section detection, contact extraction, and structure analysis.
"""

import hashlib
import re
import logging
from typing import Optional
from pathlib import Path

from app.models.document import (
    ParsedCV, ContactInfo, CVSection, ExperienceEntry,
    EducationEntry, ProjectEntry, CertificationEntry
)

logger = logging.getLogger(__name__)

# Common section heading patterns
SECTION_PATTERNS = {
    "summary": r"(?i)(professional\s+summary|summary|profile|about\s+me|objective|overview)",
    "experience": r"(?i)(work\s+experience|experience|employment|work\s+history|professional\s+experience|career\s+history)",
    "education": r"(?i)(education|academic|qualifications|degrees)",
    "skills": r"(?i)(skills|technical\s+skills|core\s+competencies|technologies|tech\s+stack|competencies)",
    "projects": r"(?i)(projects|personal\s+projects|side\s+projects|portfolio)",
    "certifications": r"(?i)(certifications|certificates|licenses|professional\s+certifications)",
    "achievements": r"(?i)(achievements|accomplishments|awards|honors)",
    "languages": r"(?i)(languages|language\s+proficiency)",
    "volunteer": r"(?i)(volunteer|volunteering|community)",
    "publications": r"(?i)(publications|papers|research)",
    "interests": r"(?i)(interests|hobbies)",
}

# Contact patterns
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}")
LINKEDIN_PATTERN = re.compile(r"(?:linkedin\.com/in/|linkedin\.com/profile/)[a-zA-Z0-9_-]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"(?:github\.com/)[a-zA-Z0-9_-]+", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")


class DocumentParserService:
    """CV/Resume parsing pipeline."""

    def parse_pdf(self, file_path: str) -> ParsedCV:
        """Parse a PDF file and extract structured CV data."""
        pages_text = []
        full_text = ""
        formatting_signals = []
        is_scanned = False
        parser_warnings = []

        # 1. Try PyMuPDF
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                text = page.get_text("text") or ""
                pages_text.append(text)
                full_text += text + "\n\n"

                # Check for images (scanned PDF detection §9)
                images = page.get_images()
                if images and len(text.strip()) < 50:
                    is_scanned = True
                    formatting_signals.append(f"Page {page_num + 1}: Image-based content detected")

                # Check for tables
                tables = page.find_tables()
                if tables and len(tables.tables) > 0:
                    formatting_signals.append("tables_detected")

            doc.close()
        except Exception as fitz_err:
            logger.warning(f"PyMuPDF failed: {fitz_err}, trying pypdf fallback...")

        # 2. Fallback to pypdf if PyMuPDF failed or produced empty text
        if not full_text.strip():
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = []
                full_text = ""
                for page in reader.pages:
                    text = page.extract_text() or ""
                    pages_text.append(text)
                    full_text += text + "\n\n"
            except Exception as pypdf_err:
                logger.error(f"pypdf fallback also failed: {pypdf_err}")

        if not full_text.strip():
            return ParsedCV(
                parser_warnings=["Unable to extract text from PDF. The document may be empty or an image-only scan."],
                raw_text="",
            )

        if is_scanned:
            parser_warnings.append(
                "Some pages appear to be image-based or scanned. "
                "Text extraction may be incomplete. Consider uploading a text-readable PDF."
            )

        # Detect multi-column layout
        if self._detect_multi_column(full_text):
            formatting_signals.append("multi_column_layout")
            parser_warnings.append("Multi-column layout detected. Some content ordering may be affected.")

        parsed = self._parse_text(full_text)
        parsed.page_count = len(pages_text)
        parsed.formatting_signals = formatting_signals
        parsed.parser_warnings.extend(parser_warnings)
        parsed.raw_text = full_text

        return parsed

    def parse_docx(self, file_path: str) -> ParsedCV:
        """Parse a DOCX file and extract structured CV data."""
        try:
            from docx import Document as DocxDocument

            doc = DocxDocument(file_path)
            full_text = ""
            formatting_signals = []

            for paragraph in doc.paragraphs:
                full_text += paragraph.text + "\n"

            # Check for tables
            if doc.tables:
                formatting_signals.append("tables_detected")
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            full_text += cell.text + " "
                    full_text += "\n"

            parsed = self._parse_text(full_text)
            parsed.page_count = max(1, len(full_text) // 3000)  # Estimate
            parsed.formatting_signals = formatting_signals
            parsed.raw_text = full_text

            return parsed

        except Exception as e:
            logger.error(f"DOCX parsing failed: {e}")
            return ParsedCV(
                parser_warnings=[f"DOCX parsing failed: {str(e)}"],
                raw_text=""
            )

    def _parse_text(self, text: str) -> ParsedCV:
        """Parse raw text into structured CV components."""
        contact = self._extract_contact(text)
        sections = self._detect_sections(text)

        return ParsedCV(
            contact=contact,
            summary=self._extract_summary(sections),
            experience=self._extract_experience(sections),
            education=self._extract_education(sections),
            skills=self._extract_skills(text, sections),
            projects=self._extract_projects(sections),
            certifications=self._extract_certifications(sections),
            achievements=self._extract_achievements(sections),
            languages=self._extract_languages(sections),
            links=self._extract_links(text),
            sections=sections,
        )

    def _extract_contact(self, text: str) -> ContactInfo:
        """Extract contact information from the first portion of text."""
        header = text[:1500]  # Contact info usually in the first section

        emails = EMAIL_PATTERN.findall(header)
        phones = PHONE_PATTERN.findall(header)
        linkedins = LINKEDIN_PATTERN.findall(header)
        githubs = GITHUB_PATTERN.findall(header)

        # Extract name (usually the first non-empty line)
        lines = [l.strip() for l in header.split("\n") if l.strip()]
        name = lines[0] if lines else None
        # Heuristic: if the first line is too long or contains @, it's not a name
        if name and (len(name) > 60 or "@" in name):
            name = None

        return ContactInfo(
            name=name,
            email=emails[0] if emails else None,
            phone=phones[0] if phones else None,
            linkedin=f"https://{linkedins[0]}" if linkedins else None,
            github=f"https://{githubs[0]}" if githubs else None,
        )

    def _detect_sections(self, text: str) -> list[CVSection]:
        """Detect and segment CV sections."""
        sections = []
        lines = text.split("\n")
        current_section = None
        current_content = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                if current_content:
                    current_content.append("")
                continue

            section_type = self._classify_heading(stripped)
            if section_type and len(stripped) < 80:
                # Save previous section
                if current_section:
                    sections.append(CVSection(
                        title=current_section["title"],
                        content="\n".join(current_content).strip(),
                        section_type=current_section["type"],
                        start_index=current_section["start"],
                        end_index=i - 1,
                    ))
                current_section = {"title": stripped, "type": section_type, "start": i}
                current_content = []
            else:
                current_content.append(stripped)

        # Save last section
        if current_section:
            sections.append(CVSection(
                title=current_section["title"],
                content="\n".join(current_content).strip(),
                section_type=current_section["type"],
                start_index=current_section["start"],
                end_index=len(lines) - 1,
            ))

        return sections

    def _classify_heading(self, text: str) -> Optional[str]:
        """Classify a line as a section heading."""
        clean = text.strip().rstrip(":")
        for section_type, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, clean):
                return section_type
        return None

    def _extract_summary(self, sections: list[CVSection]) -> str:
        """Extract professional summary."""
        for s in sections:
            if s.section_type == "summary":
                return s.content
        return ""

    def _extract_experience(self, sections: list[CVSection]) -> list[ExperienceEntry]:
        """Extract work experience entries."""
        entries = []
        for s in sections:
            if s.section_type != "experience":
                continue

            # Split by apparent job entries (lines with dates or company names)
            blocks = self._split_experience_blocks(s.content)
            for block in blocks:
                entry = self._parse_experience_block(block)
                if entry.job_title or entry.company:
                    entries.append(entry)

        return entries

    def _split_experience_blocks(self, content: str) -> list[str]:
        """Split experience section into individual job blocks."""
        lines = content.split("\n")
        blocks = []
        current_block = []
        date_pattern = re.compile(r"\d{4}|present|current", re.IGNORECASE)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_block:
                    current_block.append("")
                continue

            # Heuristic: new block starts with a line that has a date or is short (title)
            has_date = bool(date_pattern.search(stripped))
            is_short = len(stripped) < 80 and not stripped.startswith(("•", "-", "*", "–", "►"))

            if current_block and (has_date and is_short):
                blocks.append("\n".join(current_block))
                current_block = [stripped]
            else:
                current_block.append(stripped)

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _parse_experience_block(self, block: str) -> ExperienceEntry:
        """Parse a single experience block into structured data."""
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            return ExperienceEntry()

        job_title = lines[0] if lines else ""
        company = lines[1] if len(lines) > 1 else ""
        bullets = []
        technologies = []

        for line in lines[2:]:
            if line.startswith(("•", "-", "*", "–", "►", "·")):
                bullet = line.lstrip("•-*–►· ").strip()
                bullets.append(bullet)
                # Extract technologies from bullets
                techs = self._extract_techs_from_text(bullet)
                technologies.extend(techs)
            elif line and not any(line.startswith(c) for c in ["•", "-", "*"]):
                bullets.append(line)

        # Try to extract dates
        date_pattern = re.compile(r"(\w+\s+\d{4}|\d{4})\s*[-–]\s*(\w+\s+\d{4}|\d{4}|Present|Current)", re.IGNORECASE)
        start_date = None
        end_date = None
        is_current = False

        for line in lines[:3]:
            match = date_pattern.search(line)
            if match:
                start_date = match.group(1)
                end_date = match.group(2)
                is_current = end_date.lower() in ("present", "current")
                break

        return ExperienceEntry(
            job_title=job_title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            bullets=bullets,
            technologies=list(set(technologies)),
        )

    def _extract_education(self, sections: list[CVSection]) -> list[EducationEntry]:
        """Extract education entries."""
        entries = []
        for s in sections:
            if s.section_type != "education":
                continue
            lines = [l.strip() for l in s.content.split("\n") if l.strip()]
            current_entry: dict = {}

            for line in lines:
                if not line.startswith(("•", "-", "*")) and len(line) < 120:
                    if current_entry:
                        entries.append(EducationEntry(**current_entry))
                    current_entry = {"degree": line, "institution": ""}
                elif current_entry:
                    if not current_entry.get("institution"):
                        current_entry["institution"] = line.lstrip("•-* ").strip()
                    else:
                        current_entry.setdefault("achievements", []).append(line.lstrip("•-* ").strip())

            if current_entry:
                entries.append(EducationEntry(**current_entry))

        return entries

    def _extract_skills(self, text: str, sections: list[CVSection]) -> list[str]:
        """Extract skills from skills sections and throughout the CV."""
        skills = []
        for s in sections:
            if s.section_type == "skills":
                # Parse skills section
                for line in s.content.split("\n"):
                    line = line.strip().lstrip("•-*·►– ")
                    if not line:
                        continue
                    # Split by common delimiters
                    for skill in re.split(r"[,|•·]", line):
                        skill = skill.strip().strip("•-*·► ")
                        if skill and len(skill) < 50:
                            skills.append(skill)
        return list(set(skills))

    def _extract_projects(self, sections: list[CVSection]) -> list[ProjectEntry]:
        """Extract project entries."""
        entries = []
        for s in sections:
            if s.section_type != "projects":
                continue
            lines = [l.strip() for l in s.content.split("\n") if l.strip()]
            current_name = ""
            current_desc = []

            for line in lines:
                if not line.startswith(("•", "-", "*")) and len(line) < 80:
                    if current_name:
                        entries.append(ProjectEntry(
                            name=current_name,
                            description="\n".join(current_desc),
                            technologies=self._extract_techs_from_text("\n".join(current_desc)),
                        ))
                    current_name = line
                    current_desc = []
                else:
                    current_desc.append(line.lstrip("•-*·► "))

            if current_name:
                entries.append(ProjectEntry(
                    name=current_name,
                    description="\n".join(current_desc),
                    technologies=self._extract_techs_from_text("\n".join(current_desc)),
                ))

        return entries

    def _extract_certifications(self, sections: list[CVSection]) -> list[CertificationEntry]:
        """Extract certification entries."""
        entries = []
        for s in sections:
            if s.section_type != "certifications":
                continue
            for line in s.content.split("\n"):
                line = line.strip().lstrip("•-*·► ")
                if line and len(line) > 3:
                    entries.append(CertificationEntry(name=line))
        return entries

    def _extract_achievements(self, sections: list[CVSection]) -> list[str]:
        """Extract achievements."""
        achievements = []
        for s in sections:
            if s.section_type == "achievements":
                for line in s.content.split("\n"):
                    line = line.strip().lstrip("•-*·► ")
                    if line:
                        achievements.append(line)
        return achievements

    def _extract_languages(self, sections: list[CVSection]) -> list[str]:
        """Extract languages."""
        langs = []
        for s in sections:
            if s.section_type == "languages":
                for line in s.content.split("\n"):
                    for lang in re.split(r"[,|•·]", line):
                        lang = lang.strip().lstrip("•-*·► ")
                        if lang and len(lang) < 40:
                            langs.append(lang)
        return langs

    def _extract_links(self, text: str) -> list[str]:
        """Extract URLs from text."""
        return URL_PATTERN.findall(text[:3000])

    def _extract_techs_from_text(self, text: str) -> list[str]:
        """Extract technology names from text using common tech keywords."""
        # Common technology names to look for
        tech_keywords = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby",
            "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "HTML", "CSS",
            "React", "Angular", "Vue", "Next.js", "Node.js", "Express", "Django", "Flask",
            "FastAPI", "Spring", "Rails", ".NET", "Laravel",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            "Git", "Jenkins", "CI/CD", "GraphQL", "REST", "gRPC",
            "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
            "Linux", "Nginx", "Apache", "RabbitMQ", "Kafka",
        ]
        found = []
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech.lower() in text_lower:
                found.append(tech)
        return found

    def _detect_multi_column(self, text: str) -> bool:
        """Detect if the CV uses a multi-column layout."""
        lines = text.split("\n")
        wide_gap_count = 0
        for line in lines[:50]:
            if "   " in line and len(line) > 60:
                wide_gap_count += 1
        return wide_gap_count > 5

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file for deduplication (§57)."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
