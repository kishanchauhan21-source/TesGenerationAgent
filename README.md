# TesGenerationAgent

This repository provides a Python-based AI test generation agent that reads a Business Requirements Specification (BRS) document, identifies requirement details and embedded artifacts, and produces Excel-based test case sheets and a Requirement Traceability Matrix (RTM).

## What it does

- Supports `.doc`, `.docx`, and `.pdf` requirement documents.
- Detects nearby attached reference files and embedded document artifacts.
- Extracts images used within the BRS and uses them as input for the test-case generation logic.
- Generates positive, negative, boundary, and exception cases.
- Produces an Excel workbook with:
  - `TestCases` sheet
  - `RTM` sheet
  - `Regression` sheet for failed cases
- Re-runs on updated versions of the document and refreshes the outputs.
- Supports optional OpenAI/Azure OpenAI analysis when credentials are configured.

## Project structure

- `app.py` – CLI entry point for the agent
- `src/test_generation_agent/` – implementation modules

## Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the generator with a BRS file:

```bash
python app.py --input "/path/to/BRS.docx" --output-dir "/path/to/output"
```

3. The generated workbook will be saved as:

```text
/path/to/output/<document_name>_test_cases.xlsx
```

## Environment variables

Optional AI enhancement:

```bash
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="gpt-4o-mini"
```

## Typical output columns

- Req. No.
- Test Case No.
- Test case description
- Test steps
- Expected Result
- Severity of the test case
- Pass/Fail Status

## Notes

This project is designed as a working starting point for a real-world enterprise solution. In production, it can be extended with:

- JIRA integration for fetching BRS documents and attachments
- SharePoint/SMB/NAS path scanning
- OCR for scanned PDFs and images
- Excel validation workflows for execution results
- Git-based version tracking for requirement updates

