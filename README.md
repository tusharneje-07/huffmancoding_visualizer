# Huffman Coding Visualizer

Small educational Flask app that demonstrates Huffman coding. You can upload a text file or paste text, run compression, and visualize the resulting Huffman tree (SVG) — plus a bottom-up animation that replays the node merging steps used to build the tree.

Features
- Upload or type text input.
- Huffman compression and decompression (files written to `uploads/`).
- Interactive SVG tree (zoom / pan) and downloadable SVG/PNG export.
- Bottom-up canvas animation showing merge steps.

Quickstart
1. Create a Python 3 virtual environment and activate it:

   - python -m venv .venv
   - source .venv/bin/activate  # macOS / Linux
   - .venv\Scripts\activate   # Windows (PowerShell)

2. Install Flask:

   - pip install flask

3. Run the server:

   - python app.py

4. Open `http://127.0.0.1:5000` in your browser.

Detailed documentation
For a deeper explanation of the algorithm, UI design decisions, animation data, and how the project is structured, see `docs/README.md`.

Screenshots
Place two screenshots as `docs/screenshots/SS1.png` and `docs/screenshots/SS2.png` to show UI examples. The docs will reference those files.

Files
- `app.py` — Flask server and request handling
- `HuffmanCoding.py` — Huffman implementation with merge-tracing
- `templates/index.html` — frontend UI (Tailwind + D3 + Canvas)

License: MIT
