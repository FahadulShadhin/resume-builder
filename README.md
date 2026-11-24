# Resume Builder

Generate a one-page, Letter-size PDF resume from validated JSON using
[uv](https://docs.astral.sh/uv/), Pydantic, and ReportLab.

## Requirements

- Python 3.10 or newer
- uv

## Generate the resume

From the project directory:

```sh
uv run resume-builder
```

By default, the command reads `data/resume.json` and writes
`output/resume.pdf`. Use `--input` and `--output` to choose different paths:

```sh
uv run resume-builder --input data/resume.json --output output/resume.pdf
```

The JSON is validated against the models in `src/resume_builder/models.py`.
The PDF uses the section order and page-size settings from the JSON. If
`single_page` is enabled and the content does not fit, generation fails with an
actionable error instead of silently creating a multi-page resume.

## Run tests

```sh
uv run python -m unittest discover -s tests
```
