from sqlite3 import Error
from sqlite_object.sql_query import SQLQuery
from sqlite_object.sqlite_object import SQLiteObject, get_sqlite_object

# Get a object and select a table to work on.
# Using this method you will need to close the connection yourself

# This creates a singleton object
sqlite_object = get_sqlite_object("test.db")

# This creates a new object
sqlite_object = SQLiteObject("test.db")

# Create a test table
create_table_sql = """
CREATE TABLE IF NOT EXISTS tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
sqlite_object.execute(create_table_sql)

# Set the current table to work on
sqlite_object.set_table("tests")

# Insert using a dict of values
sqlite_object.insert({"title": "test"})
print(sqlite_object.rows_affected(), "rows affected")
print(sqlite_object.insert_id(), "last insert id")

# Fetch one using where string and placeholder values
row = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))
print(dict(row), "fetchone_simple")

# Or fetch one using a dict of where clauses
row = sqlite_object.fetchone_simple(where={"title": "test"})
print(dict(row), "fetchone_simple")

# You may also add order by and limit
row = sqlite_object.fetchone_simple(
    where={"title": "test"}, order_by=[("title", "DESC"), ("description", "ASC")]
)

if row:
    print(dict(row), "fetchone_simple with order, limit")

# Insert another row
sqlite_object.insert({"title": "test 2"})

# Fetchall using where string and placeholder values
rows = sqlite_object.fetchall(where="title = ?", placeholder_values=("test",))

# -> List of dicts with column names as keys and values as values
for row in rows:
    print(dict(row), "fetchall")

# Fetchall using a dict of where clauses
rows = sqlite_object.fetchall_simple(where={"title": "test"})

# Fetch all using a dict of where clause and a list of order by clause and a list of limit clause
sqlite_object.fetchall_simple(
    where={"title": "test"},
    order_by=[("title", "DESC"), ("description", "ASC")],
    limit=[0, 2],
)

# Update using a dict of values and a dict of where clauses
sqlite_object.update_simple(values={"title": "new test"}, where={"title": "test"})

# Update with values if they are found in where, otherwise insert new values
sqlite_object.replace(values={"title": "new test"}, where={"title": "test"})

# Make a custom SQL query
query = SQLQuery()
query.select("tests")
query.where("title = ?")
query.order_by([["title", "DESC"], ["description", "ASC"]])
query.limit([0, 2])
sql = query.get_query()
print("query", sql)
# -> SELECT * FROM `tests` WHERE title = ? ORDER BY `title` DESC, `description` ASC LIMIT 0, 2

# Fetch all from a custom query
sqlite_object.fetchall_query(sql, placeholder_values=("test",))

# Fetch one from a custom query
sqlite_object.fetchone_query(sql, placeholder_values=("test",))

# Delete using a dict of where clause
sqlite_object.delete_simple(where={"title": "new test"})
sqlite_object.delete_simple(where={"title": "test 2"})


# Execute in a single transaction
def test_function():
    sqlite_object.insert(values={"title": "transaction test"})
    sqlite_object.insert(
        values={"unknown_column_causing_exception": "transaction test"}
    )


try:
    sqlite_object.in_transaction_execute(test_function)
except Error as e:
    print("Exception occured as it should")
    # table tests has no column named unknown_column_causing_exception
    pass

# Get num rows
num_rows = sqlite_object.get_num_rows(where={"title": "transaction test"}, column="*")
print(num_rows, "Num rows after transaction. Should be 0")  # -> 0
# The first inserts was successful, but the second should fail
# Anything in the test_function() will be rolled back


def test_function_working():
    sqlite_object.insert(values={"title": "transaction test"})
    sqlite_object.insert(values={"title": "transaction test"})


try:
    sqlite_object.in_transaction_execute(test_function_working)
except Error as e:
    print("No error should be raised here. So you should not see this message.")
    pass

num_rows = sqlite_object.get_num_rows(where={"title": "transaction test"}, column="*")

# Both inserts were commited
print(num_rows)  # -> 2

rows = sqlite_object.fetchall_simple()
for row in rows:
    print(dict(row))

# Delete the test rows
sqlite_object.delete_simple(where={"title": "transaction test"})

# Close the connection
sqlite_object.close()
