# Manual inputs

Drop files here that agents cannot fetch themselves. Every file becomes evidence of type `manual-input`.

- `trends/<keyword>-<YYYY-MM-DD>.csv`: Google Trends export (trends.google.com, US, past 5 years, "Download CSV").
- `<product_id>/<source>-<YYYY-MM-DD>.txt|png`: pasted text or screenshots from pages that block fetching
  (Amazon, AliExpress, TikTok Creative Center, Meta Ad Library). Name the source and the date in the filename.

Agents cite these as `E-<id>` rows with `Type = manual-input` and the file path in the URL column.
