import sqlglot
from sqlglot import exp

def validate_sql(sql):

    try:
        queries = sqlglot.parse(sql, read="postgres")

        if len(queries) != 1 or queries[0] is None:
            return False

        query = queries[0]

        if not isinstance(query, exp.Select):
            return False

        tables = {
            table.name.lower()
            for table in query.find_all(exp.Table)
        }

        if not tables or not tables.issubset({"students"}):
            return False

        return True

    except Exception:
        return False