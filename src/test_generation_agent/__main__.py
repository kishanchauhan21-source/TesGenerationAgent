import re
from pathlib import Path
from typing import List

from src.test_generation_agent.ai_agent import analyze_requirements
from src.test_generation_agent.document_parser import DocumentAnalysis
from src.test_generation_agent.rtm_generator import build_rtm


def infer_requirement_numbers(doc: DocumentAnalysis) -> list[str]:
    if doc.requirements:
        return [str(item) for item in doc.requirements]

    matches = re.findall(r"(?:REQ|Requirement|Req)\s*[-\s#]*\d+", doc.text, flags=re.IGNORECASE)
    if matches:
        return [match.strip() for match in matches]

    return ["REQ-1"]


def _normalize_title(raw: str) -> str:
    return raw.strip() or "Business requirement validation"


def generate_test_cases(doc: DocumentAnalysis):
    requirement_numbers = infer_requirement_numbers(doc)
    requirements = analyze_requirements(doc.text, [artifact.name for artifact in doc.attachments], [artifact.name for artifact in doc.images])

    generated_cases: list[dict] = []
    regression_cases: list[dict] = []
    idx = 1

    for requirement in requirements:
        req_no = requirement.get("req_no") or requirement_numbers[min(len(requirement_numbers) - 1, 0)]
        title = requirement.get("title") or f"Requirement {req_no}"
        description = requirement.get("description") or title
        req_text = _normalize_title(description)

        for category, severity in [("Positive", "Medium"), ("Negative", "High"), ("Boundary", "Medium"), ("Exception", "High")]:
            test_case_no = f"TC-{idx:03d}"
            case = {
                "Req. No.": req_no,
                "Test Case No.": test_case_no,
                "Test case description": f"{title}: {category} scenario for {req_text}",
                "Test steps": "1. Open the BRS input and review requirement details. 2. Execute the business flow. 3. Validate the result against expected behavior.",
                "Expected Result": f"The system handles the {category.lower()} scenario correctly and meets the requirement objective.",
                "Severity of the test case": severity,
                "Pass/Fail Status": "Not Executed",
            }
            generated_cases.append(case)
            regression_cases.append(case)
            idx += 1

    rtm_rows = build_rtm(generated_cases)
    return generated_cases, rtm_rows, regression_cases


def generate_regression_from_execution(execution_file: str | Path, test_cases: list[dict]) -> list[dict]:
    from openpyxl import load_workbook

    workbook_path = Path(execution_file)
    if not workbook_path.exists():
        raise FileNotFoundError(f"Execution file not found: {workbook_path}")

    wb = load_workbook(workbook_path, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    failed_rows = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        values = dict(zip(headers, row))
        if str(values.get("Pass/Fail Status")).lower() == "fail":
            failed_rows.append(values)

    regression_cases = []
    for failed in failed_rows:
        for case in test_cases:
            if case.get("Test Case No.") == failed.get("Test Case No."):
                scenario = dict(case)
                scenario["Test case description"] = f"Regression scenario for failed case: {case.get('Test case description')}"
                scenario["Pass/Fail Status"] = "Not Executed"
                regression_cases.append(scenario)
                break

    if not regression_cases:
        return []
    return regression_cases


__all__ = ["generate_test_cases", "generate_regression_from_execution"]

