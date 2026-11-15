#!/usr/bin/env python3

import argparse
from pathlib import Path

from src.test_generation_agent.document_parser import parse_document
from src.test_generation_agent.test_case_generator import generate_test_cases
from src.test_generation_agent.excel_exporter import save_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test cases from a Business Requirements document.")
    parser.add_argument("--input", required=True, help="Path to BRS document (.doc, .docx, .pdf)")
    parser.add_argument("--output-dir", required=True, help="Directory to save generated XLSX files")
    parser.add_argument("--jira-url", default=None, help="Optional JIRA endpoint to use for document retrieval")
    parser.add_argument("--generate-regression", action="store_true", help="Generate regression scenarios from failed cases")
    parser.add_argument("--execution-file", default=None, help="Optional Excel file with executed test results")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    document = parse_document(input_path)
    test_cases, rtm_rows, regression_rows = generate_test_cases(document)
    workbook_path = save_workbook(output_dir, input_path.name, test_cases, rtm_rows, regression_rows)

    if args.generate_regression:
        if args.execution_file:
            from src.test_generation_agent.test_case_generator import generate_regression_from_execution

            regression_rows = generate_regression_from_execution(args.execution_file, test_cases)
            save_workbook(output_dir, input_path.name, test_cases, rtm_rows, regression_rows, include_regression=True)
        else:
            print("No execution file supplied; regression file was not generated.")

    print(f"Created: {workbook_path}")


if __name__ == "__main__":
    main()

