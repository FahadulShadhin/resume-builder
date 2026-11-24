# Agent instructions

## Project purpose

This project validates resume JSON with Pydantic and generates a PDF with ReportLab. The reference design is `data/Fahadul_Shadhin_Resume_2026.pdf`; the default input is `data/resume.json`.

## Workflow

- Read the relevant models, renderer, tests, and input data before changing behavior.
- Keep changes focused. Preserve the existing resume content and visual style unless the task requests otherwise.
- Treat `data/resume.json` as user content: do not rewrite or reformat it as part of unrelated code changes.
- Keep model validation and PDF rendering responsibilities separate. Add or update focused tests for behavior changes.
- Use `uv` for project and dependency commands. Avoid adding dependencies when the existing stack can do the job.
- Do not silently hide invalid input or PDF layout failures; keep errors clear and actionable.

## Validation

Run the test suite after code changes:

```sh
uv run python -m unittest discover -s tests -v
```

For changes to PDF generation or input handling, also generate a PDF and check that it opens and respects `settings.single_page`:

```sh
uv run resume-builder --input data/resume.json --output output/resume.pdf
```

When modifying layout, inspect the rendered PDF against the reference design, not just whether a file was created.

## Project map

- `src/resume_builder/models.py`: validated resume schema and accepted input field names.
- `src/resume_builder/pdf.py`: ReportLab layout and PDF generation.
- `src/resume_builder/cli.py`: command-line arguments and user-facing errors.
- `data/`: sample resume JSON and visual reference PDF.
- `tests/`: automated tests.
