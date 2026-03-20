# Huffman Coding Visualizer

Simple Flask-based Huffman coding visualizer. Upload a text file or paste/enter text, compress using Huffman coding, visualize the top-down tree, and watch a bottom-up merge animation of the tree construction. Includes export (SVG/PNG) and compressed file download.

Usage
1. Create and activate a Python virtualenv
2. Install Flask: `pip install flask`
3. Run: `python app.py`
4. Open `http://127.0.0.1:5000`

Files
- `app.py` — Flask application
- `HuffmanCoding.py` — Huffman algorithm and merge step tracing
- `templates/index.html` — single-file UI (Tailwind + D3 + Canvas animation)

License: MIT
