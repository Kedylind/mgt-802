# Casebook Setup Guide

## Overview

The case generator can work with or without a casebook PDF. If you have a casebook PDF, the system will use RAG (Retrieval-Augmented Generation) to create more realistic cases based on real examples.

## Adding a Casebook PDF

### Step 1: Place the PDF File

Place your casebook PDF file in one of these locations (the system will check in order):

1. **Project root** (recommended):
   ```
   mgt-802/
   └── Darden-Case-Book-2018-2019.pdf
   ```

2. **Alternative locations** (also checked):
   - `mgt-802/casebook.pdf`
   - `mgt-802/docs/Darden-Case-Book-2018-2019.pdf`
   - `mgt-802/static/Darden-Case-Book-2018-2019.pdf`

### Step 2: Verify the File

The system will automatically detect the PDF when you generate a case. You'll see a message in the console:
```
Casebook loaded from: /path/to/your/casebook.pdf
```

If no casebook is found, you'll see:
```
Warning: No casebook PDF found. Case generation will proceed without RAG.
```

### Step 3: Test Case Generation

1. Go to the "Generate Case" page
2. Enter a topic (e.g., "Airline Profitability")
3. Select case type
4. Click "Generate Case"

The system will:
- **With casebook**: Use RAG to search for similar cases and create a more realistic case
- **Without casebook**: Still generate a case using AI, but without reference examples

## Supported PDF Formats

- Standard PDF files (`.pdf`)
- Text-based PDFs work best (scanned PDFs may have limited functionality)
- Recommended: Darden Case Book or similar case study collections

## Troubleshooting

### PDF Not Detected

1. Check file location matches one of the paths above
2. Verify file name matches exactly (case-sensitive on some systems)
3. Check file permissions (must be readable)

### PDF Tool Errors

If you see errors loading the PDF tool:
- Ensure the PDF is not corrupted
- Try a different PDF file
- Check that `crewai-tools` is installed: `pip install crewai-tools`

### Generation Works Without PDF

This is normal! The system will generate cases even without a casebook, just without the RAG enhancement.

## Benefits of Using a Casebook

With a casebook PDF:
- ✅ More realistic case structures
- ✅ Industry-standard frameworks
- ✅ Better exhibit formatting
- ✅ Authentic case narratives
- ✅ Reference to real case examples

Without a casebook:
- ✅ Still generates quality cases
- ✅ Uses AI knowledge of case interviews
- ✅ Faster generation (no PDF search step)
- ✅ Works immediately without setup

## Next Steps

Once your casebook is set up:
1. Generate a few test cases
2. Compare cases generated with and without the casebook
3. Adjust topics to match your casebook's content for best results

