from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sqlalchemy import text
from database import engine
from agent import generate_sql
from sql_validator import validate_sql
import time

app = Flask(__name__)
CORS(app)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student SQL AI</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 16px; background: #0f172a; color: #e2e8f0; }
        h1 { margin-bottom: 8px; }
        p.sub { color: #94a3b8; margin-top: 0; }
        form { display: flex; gap: 8px; margin: 20px 0; }
        input { flex: 1; padding: 10px 12px; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: #f8fafc; font-size: 15px; }
        button { padding: 10px 18px; border-radius: 6px; border: none; background: #3b82f6; color: white; font-size: 15px; cursor: pointer; }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        pre { background: #1e293b; padding: 12px; border-radius: 6px; overflow-x: auto; border: 1px solid #334155; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; background: #1e293b; border-radius: 6px; overflow: hidden; }
        th, td { padding: 8px 12px; border-bottom: 1px solid #334155; text-align: left; }
        th { background: #334155; }
        .error { color: #f87171; }
    </style>
</head>
<body>
    <h1>Student SQL AI</h1>
    <p class="sub">Ask a question about the <code>students</code> table.</p>
    <form id="query-form">
        <input id="question" type="text" placeholder="e.g. Kashish registration number" required />
        <button id="submit-btn" type="submit">Ask</button>
    </form>
    <div id="output"></div>
    <script>
        const form = document.getElementById("query-form");
        const input = document.getElementById("question");
        const button = document.getElementById("submit-btn");
        const output = document.getElementById("output");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            button.disabled = true;
            output.innerHTML = "<p>Running query...</p>";
            try {
                const res = await fetch("/api/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: input.value })
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    output.innerHTML = `<p class="error">${data.error || "Request failed"}</p>`;
                    return;
                }
                let html = `<p><strong>Generated SQL:</strong></p><pre>${data.generated_sql}</pre>`;
                html += `<p>Rows: ${data.row_count} (${data.execution_time}s)</p>`;
                if (data.results.length > 0) {
                    const cols = Object.keys(data.results[0]);
                    html += "<table><thead><tr>" + cols.map(c => `<th>${c}</th>`).join("") + "</tr></thead><tbody>";
                    html += data.results.map(r => "<tr>" + cols.map(c => `<td>${r[c] ?? ""}</td>`).join("") + "</tr>").join("");
                    html += "</tbody></table>";
                }
                output.innerHTML = html;
            } catch (err) {
                output.innerHTML = `<p class="error">${err.message}</p>`;
            } finally {
                button.disabled = false;
            }
        });
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return jsonify({
            "status": "connected",
            "database": "student_ai"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def query_database():
    start = time.time()

    try:
        data = request.get_json(silent=True) or {}
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Please enter a question"}), 400

        sql = generate_sql(question)

        if not validate_sql(sql):
            return jsonify({
                "error": "Unsafe or invalid SQL generated",
                "generated_sql": sql
            }), 400

        with engine.connect() as connection:
            with connection.begin():
                connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                connection.exec_driver_sql("SET LOCAL statement_timeout = '5000'")

                result = connection.execute(text(sql))
                rows = result.mappings().fetchmany(100)

                records = [
                    {
                        key: str(value) if value is not None else None
                        for key, value in row.items()
                    }
                    for row in rows
                ]

        return jsonify({
            "success": True,
            "question": question,
            "generated_sql": sql,
            "results": records,
            "row_count": len(records),
            "execution_time": round(time.time() - start, 3)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
