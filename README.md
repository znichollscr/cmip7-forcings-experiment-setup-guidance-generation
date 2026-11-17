# CMIP7 Forcings Guidance Generation

Tooling for generating the CMIP7 experiment setup and forcings guidance pages
in the sibling `cmip7-guidance` repository.

The generator keeps repeated information, such as forcing reference links,
source IDs, shared setup language, index entries, and CMIP7 controlled
vocabulary metadata, in one Python source of truth. Rendering is done with
plain Python rather than a templating dependency.

## Installation

This repository uses [uv](https://docs.astral.sh/uv/) for environment
management. To create the virtual environment, run:

```sh
uv sync
uv run esgvoc use cmip7@latest
uv run pre-commit install
```

The same steps are available via:

```sh
make virtual-environment
```

To update only the local CMIP7 controlled vocabulary cache, run:

```sh
make update-cvs
```

## Usage

To regenerate the markdown files in the default sibling documentation
repository path:

```sh
make generate-guidance
```

This writes to:

```text
../cmip7-guidance/docs/CMIP7/Experiment_set_up_and_Forcings
```

Free text from the CMIP7 CVs (descriptions and citations) can contain LaTeX
(e.g. `H\"ogner` or `{\textdegree}C`) and HTML entities.
This is converted to plain text as part of generation using
[pylatexenc](https://pylatexenc.readthedocs.io/)
(see `src/local/cv_text.py`).

To check whether the generated files are up to date:

```sh
make check-guidance
```

You can also run the drive script directly and choose another output directory:

```sh
uv run python scripts/generate_guidance_docs.py --output-dir /tmp/cmip7-guidance
uv run python scripts/generate_guidance_docs.py --output-dir /tmp/cmip7-guidance --check
```

## Repository Structure

- `scripts/generate_guidance_docs.py`: command-line entrypoint.
- `src/local/guidance.py`: page models, shared guidance snippets, page
  aggregation, and file writing/checking functionality.
- `src/local/rendering.py`: markdown rendering helpers.
- `src/local/branching.py`: parent/branching text helpers.
- `src/local/tags.py`: tag definitions applied to experiment pages.
- `src/local/vocab.py`: access helpers for CMIP7 metadata from `esgvoc`.
- `src/local/cv_text.py`: conversion of LaTeX/HTML markup in CV text to
  markdown (via pylatexenc).
- `src/local/forcing_references.py`: forcing reference-page definitions.
- `src/local/forcings/`: forcing specifications for each experiment.
- `src/local/activity_pages/`: experiment page definitions grouped by
  responsible activity.
- `Makefile`: convenience targets for generating, checking, and development
  setup.
