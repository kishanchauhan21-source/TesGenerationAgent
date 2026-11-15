import json
import os
import re
from typing import Any, Dict, List


def build_llm_prompt(document_text: str, attachments: List[str], images: List[str]) -> str:
    return f"""
You are an expert QA automation analyst. Extract requirements from the following business requirements document.

Document text:
{document_text[:8000]}

Attached files:
{', '.join(attachments) if attachments else 'None'}

Images found:
{', '.join(images) if images else 'None'}

Return a JSON object with a list of requirements. Each item should contain:
- req_no
- title
- description
- priority
- test_focus
"""


def analyze_with_openai(document_text: str, attachments: List[str], images: List[str]) -> List[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = build_llm_prompt(document_text, attachments, images)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200,
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        return payload.get("requirements", [])
    except Exception:
        return []


def fallback_requirement_analysis(document_text: str, attachments: List[str], images: List[str]) -> List[Dict[str, Any]]:
    sentences = re.split(r"(?<=[.!?])\s+", document_text.strip())
    requirements: List[Dict[str, Any]] = []
    idx = 1

    for sentence in sentences:
        if len(sentence) < 30:
            continue
        item = {
            "req_no": f"REQ-{idx}",
            "title": f"Business requirement {idx}",
            "description": sentence.strip(),
            "priority": "Medium",
            "test_focus": "Functionality check",
        }
        requirements.append(item)
        idx += 1

    if not requirements:
        requirements.append(
            {
                "req_no": "REQ-1",
                "title": "Core business requirement",
                "description": "The system must generate test cases from the supplied requirements document and produce an Excel-based RTM.",
                "priority": "High",
                "test_focus": "Positive, negative, boundary, exception coverage",
            }
        )

    if attachments:
        requirements[0]["description"] += " Attachments were detected and should be reviewed for reference information."
    if images:
        requirements[0]["description"] += " Embedded images were detected and should be validated as part of the requirement understanding."

    return requirements


def analyze_requirements(document_text: str, attachments: List[str], images: List[str]) -> List[Dict[str, Any]]:
    llm_results = analyze_with_openai(document_text, attachments, images)
    if llm_results:
        return llm_results
    return fallback_requirement_analysis(document_text, attachments, images)
