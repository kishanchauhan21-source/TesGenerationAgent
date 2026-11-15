def build_rtm(test_cases: list[dict]) -> list[dict]:
    rows = []
    for case in test_cases:
        rows.append({
            "Req. No.": case.get("Req. No."),
            "Test Case No.": case.get("Test Case No."),
            "Coverage Type": "Requirement coverage",
            "Status": "Covered",
        })
    return rows
