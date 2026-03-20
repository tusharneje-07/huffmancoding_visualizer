import os
import uuid

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from HuffmanCoding import HuffmanCoding


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def pretty_char(ch):
    special = {
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
        " ": "[space]",
    }
    return special.get(ch, ch)


def tree_to_dict(node, edge="root"):
    if node is None:
        return None

    children = []
    child_freq_sum = 0
    if node.left is not None:
        child = tree_to_dict(node.left, "0")
        if child is not None:
            children.append(child)
            child_freq_sum += child["freq"]
    if node.right is not None:
        child = tree_to_dict(node.right, "1")
        if child is not None:
            children.append(child)
            child_freq_sum += child["freq"]

    node_freq = node.freq if node.char is not None else child_freq_sum

    if node.char is None:
        name = f"Internal ({node_freq})"
    else:
        name = f"{pretty_char(node.char)} ({node_freq})"

    result = {
        "name": name,
        "freq": node_freq,
        "edge": edge,
        "children": children,
    }
    return result


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        return file.read()


def write_text(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def build_merge_steps(steps):
    formatted = []
    for step in steps:
        left = step.get("left", {})
        right = step.get("right", {})
        parent = step.get("parent", {})

        def normalize(node):
            char = node.get("char")
            return {
                "id": node.get("id"),
                "char": pretty_char(char) if char is not None else None,
                "freq": node.get("freq", 0),
                "is_leaf": node.get("is_leaf", False),
            }

        formatted.append(
            {
                "left": normalize(left),
                "right": normalize(right),
                "parent": normalize(parent),
            }
        )
    return formatted


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "error": None,
        "uploaded_text": None,
        "encoded_preview": None,
        "encoded_total_bits": None,
        "tree_data": None,
        "stats": None,
        "code_table": [],
        "filename": None,
        "compressed_filename": None,
        "merge_steps": [],
    }

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        direct_text = request.form.get("direct_text", "")
        has_file = (
            uploaded_file is not None and (uploaded_file.filename or "").strip() != ""
        )
        has_text = direct_text.strip() != ""

        safe_name = None
        saved_path = None

        if has_file and has_text:
            context["error"] = (
                "Please provide either a file upload or typed text, not both."
            )
            return render_template("index.html", **context)
        if has_text:
            safe_name = "typed_input.txt"
            unique_name = f"{uuid.uuid4().hex}_{safe_name}"
            saved_path = os.path.join(UPLOAD_DIR, unique_name)
            write_text(saved_path, direct_text)
        elif has_file:
            file_obj = uploaded_file
            if file_obj is None:
                context["error"] = (
                    "Uploaded file was not received properly. Please try again."
                )
                return render_template("index.html", **context)

            safe_name = secure_filename(file_obj.filename or "uploaded.txt")
            unique_name = f"{uuid.uuid4().hex}_{safe_name}"
            saved_path = os.path.join(UPLOAD_DIR, unique_name)
            file_obj.save(saved_path)
        else:
            context["error"] = "Please upload a file or type text to process."
            return render_template("index.html", **context)

        try:
            uploaded_text = read_text(saved_path)

            huffman = HuffmanCoding(saved_path)
            compressed_path = huffman.compress()
            decompressed_path = huffman.decompress(compressed_path)

            encoded_text = (
                huffman.get_encoded_text(uploaded_text) if uploaded_text else ""
            )
            encoded_preview = encoded_text[:2000]
            if len(encoded_text) > 2000:
                encoded_preview += "\n... (truncated)"

            frequency = huffman.make_freq_dict(uploaded_text)
            code_table = []
            for char, code in huffman.codes.items():
                code_table.append(
                    {
                        "char": pretty_char(char),
                        "code": code,
                        "freq": frequency.get(char, 0),
                    }
                )

            code_table.sort(key=lambda row: row["freq"], reverse=True)

            original_size = os.path.getsize(saved_path)
            compressed_size = os.path.getsize(compressed_path)
            decompressed_size = os.path.getsize(decompressed_path)

            context.update(
                {
                    "filename": safe_name,
                    "compressed_filename": os.path.basename(compressed_path),
                    "uploaded_text": uploaded_text,
                    "encoded_preview": encoded_preview,
                    "encoded_total_bits": len(encoded_text),
                    "tree_data": tree_to_dict(huffman.root),
                    "merge_steps": build_merge_steps(huffman.merge_steps),
                    "stats": {
                        "original": original_size,
                        "compressed": compressed_size,
                        "decompressed": decompressed_size,
                    },
                    "code_table": code_table,
                }
            )
        except Exception as exc:
            context["error"] = f"Processing failed: {exc}"

    return render_template("index.html", **context)


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
