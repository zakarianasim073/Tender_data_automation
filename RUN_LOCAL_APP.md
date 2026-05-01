# Run TenderFlow Local

## Start everything

Double-click:

```text
start_local_full_app.bat
```

This opens two windows:

1. `TenderFlow Backend`
   - Uses the project-local `.venv`, not your broken global Python packages
   - Starts FastAPI at `http://127.0.0.1:8001`

2. `TenderFlow Frontend`
   - Installs/checks frontend dependencies
   - Starts Vite at `http://127.0.0.1:5173`

Open:

```text
http://127.0.0.1:5173
```

## Verify backend

Open this in the browser:

```text
http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"healthy","version":"1.0.0"}
```

## Use actual processing

On the landing page, go to `Actual processing` and upload at least:

- Notice PDF
- TDS PDF
- BOQ PDF

The backend saves files into:

```text
tender_engine/input/<tender_id>/
```

Generated files are saved into:

```text
tender_engine/output/<tender_id>/
```

Download links are served through:

```text
http://127.0.0.1:8001/generated/<tender_id>/<filename>
```

## If it does not work

Check the backend window first. Common causes:

- Port `8001` already in use
- Missing template files from `tender_engine/templates/docx`
- PDF parser cannot read a scanned/non-text PDF

Check the frontend window second. Common causes:

- Port `5173` already in use
- npm install failed
- Vite dependency missing
