# OPH Book Source

This directory contains the canonical Markdown source for the OPH book:

- `prologue.md`
- `chapter-01-*.md` through `chapter-19-*.md`
- `epilogue.md`

## Print PDF Build

The polished print-style PDF is built with:

```bash
cd reverse-engineering-reality
python3 tools/build_book_pdf.py
```

This writes the finished PDF to the workspace root as:

- `../reverse-engineering-reality-book.pdf`

The build also writes temporary intermediate files under:

- `../temp/book_pdf_build/`

## Requirements

The builder expects these tools to be available in `PATH`:

- `pandoc`
- `tectonic`
- `rsvg-convert`

## Layout And Styling

The book PDF builder is implemented in:

- `tools/build_book_pdf.py`

The LaTeX header and print styling live in:

- `tools/book_pdf_header.tex`

Current output style:

- trade-book trim (`6in x 9in`)
- two-sided layout
- chapter-level table of contents
- widow/orphan control
- running headers
- tightened long-table handling for summary tables

## Notes

- The builder automatically combines the prologue, numbered chapters, and epilogue in order.
- Unnumbered front/back matter gets corrected running heads (`Prologue`, `Epilogue`).
- SVG assets referenced by the book are converted to PDF during the build.
- A few long inline scientific expressions are normalized into TeX-safe forms before compilation.
