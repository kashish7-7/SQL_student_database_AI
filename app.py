from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import text
from database import engine
from agent import generate_sql
from sql_validator import validate_sql
import time

app = Flask(__name__)
CORS(app)


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
