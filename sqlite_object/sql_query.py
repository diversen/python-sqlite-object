class SQLQuery:

    def __init__(self, table: str = None):
        self.sql = ""
        self.table = table
        self.placeholder_values = []

    def columns_as_str(self, columns):
        if isinstance(columns, list):
            columns = ", ".join(columns)  # Avoid backticks for SQLite compatibility
        return columns

    def select(self, table: str, columns='*'):
        columns = self.columns_as_str(columns)
        self.sql = f"SELECT {columns} FROM {table}"
        return self

    def where(self, where: str = None):
        if where:
            self.sql += f" WHERE {where}"
        return self

    def where_simple(self, where: dict = None):
        if not where:
            return self

        columns, values = self.get_columns_and_values(where)
        self.append_placeholder_values(values)

        where_clauses = [f"{column} = ?" for column in columns]
        where_statement = " AND ".join(where_clauses)
        self.sql += f" WHERE {where_statement}"
        return self

    def order_by(self, order_specifications: list = None):
        if order_specifications:
            order_by = ", ".join([f"{col} {dir}" for col, dir in order_specifications])
            self.sql += f" ORDER BY {order_by}"
        return self

    def limit(self, limit_values: list = None):
        if limit_values:
            self.sql += f" LIMIT {limit_values[0]}, {limit_values[1]}"
        return self

    def insert(self, table: str, values: dict):
        columns, val = self.get_columns_and_values(values)
        self.append_placeholder_values(val)

        placeholders = ", ".join(["?" for _ in columns])
        columns_formatted = ", ".join(columns)
        self.sql = f"INSERT INTO {table} ({columns_formatted}) VALUES ({placeholders})"
        return self

    def update(self, table: str, values: dict):
        columns, val = self.get_columns_and_values(values)
        self.append_placeholder_values(val)

        set_clauses = [f"{col} = ?" for col in columns]
        set_statement = ", ".join(set_clauses)
        self.sql = f"UPDATE {table} SET {set_statement}"
        return self
    
    def update_simple(self, table: str, values: dict, where: dict = None):

        self.update(table, values)
        self.where_simple(where)

        return self

    def delete(self, table: str, where=None):
        self.sql = f"DELETE FROM {table}"
        if where:
            self.where(where)
        return self

    def get_query(self):
        sql, self.sql = self.sql, ""
        return sql

    def get_placeholder_values(self):
        values, self.placeholder_values = self.placeholder_values, []
        return values

    def append_placeholder_values(self, values):
        self.placeholder_values += values

    def get_columns_and_values(self, dict_data):
        columns = list(dict_data.keys())
        values = list(dict_data.values())
        return columns, values
