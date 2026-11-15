from pathlib import Path

from openpyxl import Workbook


def _apply_header_style(ws):
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)
        cell.fill = cell.fill.copy(type="solid", start_color="D9EAF7")
        cell.alignment = cell.alignment.copy(horizontal="center")


def save_workbook(output_dir: Path, original_name: str, test_cases: list[dict], rtm_rows: list[dict], regression_rows: list[dict], include_regression: bool = True) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = original_name.replace(" ", "_").replace(".", "_")
    workbook_path = output_dir / f"{safe_name}_test_cases.xlsx"

    wb = Workbook()
    ws_cases = wb.active
    ws_cases.title = "TestCases"
    case_headers = [
        "Req. No.",
        "Test Case No.",
        "Test case description",
        "Test steps",
        "Expected Result",
        "Severity of the test case",
        "Pass/Fail Status",
    ]
    ws_cases.append(case_headers)
    for row in test_cases:
        ws_cases.append([
            row.get("Req. No."),
            row.get("Test Case No."),
            row.get("Test case description"),
            row.get("Test steps"),
            row.get("Expected Result"),
            row.get("Severity of the test case"),
            row.get("Pass/Fail Status"),
        ])
    _apply_header_style(ws_cases)

    ws_rtm = wb.create_sheet("RTM")
    rtm_headers = ["Req. No.", "Test Case No.", "Coverage Type", "Status"]
    ws_rtm.append(rtm_headers)
    for row in rtm_rows:
        ws_rtm.append([row.get("Req. No."), row.get("Test Case No."), row.get("Coverage Type"), row.get("Status")])
    _apply_header_style(ws_rtm)

    if include_regression and regression_rows:
        ws_regression = wb.create_sheet("Regression")
        regression_headers = [
            "Req. No.",
            "Test Case No.",
            "Test case description",
            "Test steps",
            "Expected Result",
            "Severity of the test case",
            "Pass/Fail Status",
        ]
        ws_regression.append(regression_headers)
        for row in regression_rows:
            ws_regression.append([
                row.get("Req. No."),
                row.get("Test Case No."),
                row.get("Test case description"),
                row.get("Test steps"),
                row.get("Expected Result"),
                row.get("Severity of the test case"),
                row.get("Pass/Fail Status"),
            ])
        _apply_header_style(ws_regression)

    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = cell.font.copy(bold=True)
        ws.freeze_panes = "A2"

    wb.save(workbook_path)
    return workbook_path
