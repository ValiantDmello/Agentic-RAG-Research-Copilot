# RAG ingestion test fixtures

All files in this directory are intentionally small and designed for pytest-based ingestion tests. The app currently supports `.txt`, `.md`, and `.pdf`; files in `unsupported/` are negative-test inputs.

## Directory layout

- `supported_text/` - supported `.txt` and `.md` fixtures for plain-text extraction, blank handling, whitespace stripping, Unicode, punctuation, single-line content, longer content, and uppercase extensions.
- `supported_pdf/` - real PDFs with extractable text, blank pages, multiple pages, and uppercase extensions.
- `unsupported/` - real or placeholder unsupported formats: DOCX, CSV, JSON, HTML, Python, PNG, JPG, ZIP, EXE, and BIN.
- `odd_names/` - supported files with spaces, mixed-case extensions, multiple dots, uppercase names, hyphens, underscores, and digits.
- `encoding/` - UTF-8 accents, symbols, newline-only content, tab/space content, and invalid UTF-8 bytes for `errors="replace"` behavior.

## Fixture inventory and purpose

### Supported plain text

| File | Purpose |
|---|---|
| `supported_text/sample.txt` | Normal multi-line `.txt` extraction. |
| `supported_text/sample.md` | Markdown headings, bullets, and paragraphs. |
| `supported_text/blank.txt` | Empty text file handling. |
| `supported_text/blank.md` | Empty markdown file handling. |
| `supported_text/whitespace_only.txt` | Whitespace-only `.txt` stripping/blank detection. |
| `supported_text/whitespace_only.md` | Whitespace-only `.md` stripping/blank detection. |
| `supported_text/leading_trailing_spaces.txt` | Leading/trailing whitespace trimming. |
| `supported_text/leading_trailing_spaces.md` | Markdown whitespace trimming around heading/paragraph text. |
| `supported_text/uppercase_extension.TXT` | Case-insensitive `.txt` extension support. |
| `supported_text/uppercase_extension.MD` | Case-insensitive `.md` extension support. |
| `supported_text/unicode_text.txt` | Multilingual Unicode and emoji extraction. |
| `supported_text/special_chars.txt` | Symbols, punctuation, quotes, and escapes. |
| `supported_text/single_line.txt` | Single-line extraction. |
| `supported_text/longer_text.txt` | Longer content for chunking or completeness assertions. |

### Supported PDFs

| File | Purpose |
|---|---|
| `supported_pdf/sample.pdf` | Basic one-page PDF text extraction. |
| `supported_pdf/multi_page.pdf` | Multi-page extraction and page-number metadata. |
| `supported_pdf/blank.pdf` | Blank PDF handling. |
| `supported_pdf/blank_first_page_then_text.pdf` | Blank first page followed by text; tests blank-page skipping with page numbers. |
| `supported_pdf/text_then_blank_page.pdf` | Text page followed by blank page; tests trailing blank-page handling. |
| `supported_pdf/whitespace_like_text.pdf` | Page containing whitespace-like text only; extractor-dependent whitespace behavior. |
| `supported_pdf/uppercase_extension.PDF` | Case-insensitive `.pdf` extension support. |

### Unsupported formats

| File | Purpose |
|---|---|
| `unsupported/sample.docx` | Valid DOCX that should be rejected as unsupported. |
| `unsupported/sample.csv` | CSV should be rejected. |
| `unsupported/sample.json` | JSON should be rejected. |
| `unsupported/sample.html` | HTML should be rejected. |
| `unsupported/sample.py` | Source code should be rejected. |
| `unsupported/sample.png` | Image should be rejected. |
| `unsupported/sample.jpg` | Image should be rejected. |
| `unsupported/sample.zip` | Archive should be rejected. |
| `unsupported/sample.exe` | Executable-like bytes should be rejected. |
| `unsupported/sample.bin` | Binary bytes should be rejected. |

### Odd filenames

| File | Purpose |
|---|---|
| `odd_names/file with spaces.txt` | Path handling for spaces. |
| `odd_names/mixed.Case.Md` | Mixed-case markdown extension. |
| `odd_names/notes.v1.txt` | Multiple dots/version-style names. |
| `odd_names/README.TEST.MD` | Uppercase multi-segment markdown filename. |
| `odd_names/weird-name_123.txt` | Hyphen, underscore, and digits. |

### Encoding/content edge cases

| File | Purpose |
|---|---|
| `encoding/utf8_accents.txt` | UTF-8 accented characters. |
| `encoding/symbols_punctuation.txt` | Symbols and punctuation. |
| `encoding/newlines_only.txt` | File containing only newlines. |
| `encoding/tabs_and_spaces.txt` | Tabs and spaces. |
| `encoding/invalid_utf8_bytes.txt` | Invalid bytes for `errors="replace"` tests. |

## Suggested pytest mapping

| Test case | Fixture paths |
|---|---|
| Supported extension validation | `supported_text/sample.txt`, `supported_text/sample.md`, `supported_pdf/sample.pdf` |
| Case-insensitive extension validation | `supported_text/uppercase_extension.TXT`, `supported_text/uppercase_extension.MD`, `supported_pdf/uppercase_extension.PDF`, `odd_names/mixed.Case.Md`, `odd_names/README.TEST.MD` |
| Unsupported extension rejection | Every file in `unsupported/` |
| Basic plain-text extraction | `supported_text/sample.txt`, `supported_text/single_line.txt`, `supported_text/longer_text.txt` |
| Markdown text extraction | `supported_text/sample.md`, `odd_names/mixed.Case.Md`, `odd_names/README.TEST.MD` |
| Blank and empty handling | `supported_text/blank.txt`, `supported_text/blank.md`, `supported_pdf/blank.pdf` |
| Whitespace stripping / blank-after-strip handling | `supported_text/whitespace_only.txt`, `supported_text/whitespace_only.md`, `encoding/newlines_only.txt`, `encoding/tabs_and_spaces.txt`, `supported_pdf/whitespace_like_text.pdf` |
| Leading/trailing whitespace trimming | `supported_text/leading_trailing_spaces.txt`, `supported_text/leading_trailing_spaces.md` |
| Unicode and encoding | `supported_text/unicode_text.txt`, `encoding/utf8_accents.txt`, `encoding/symbols_punctuation.txt`, `encoding/invalid_utf8_bytes.txt` |
| PDF text extraction | `supported_pdf/sample.pdf`, `supported_pdf/uppercase_extension.PDF` |
| PDF page-number metadata | `supported_pdf/multi_page.pdf`, `supported_pdf/blank_first_page_then_text.pdf`, `supported_pdf/text_then_blank_page.pdf` |
| Blank PDF page skipping | `supported_pdf/blank.pdf`, `supported_pdf/blank_first_page_then_text.pdf`, `supported_pdf/text_then_blank_page.pdf` |
| Path/name handling | Every file in `odd_names/` plus `supported_text/uppercase_extension.TXT` |

## Notes

- PDF page text includes source/page markers so tests can assert both extracted content and metadata.
- `supported_pdf/whitespace_like_text.pdf` may extract as empty text or whitespace depending on the PDF parser. It is best used for strip/blank behavior rather than exact raw extraction assertions.
- `encoding/invalid_utf8_bytes.txt` is intentionally not valid UTF-8. Read it with `errors="replace"` when testing replacement-character behavior.
- `generate_fixtures.py` can recreate this fixture set from scratch.
