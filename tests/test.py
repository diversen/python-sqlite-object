import sys

sys.path.append(".")

import unittest
from sqlite3 import Error
from sqlite_object.sql_query import SQLQuery
from sqlite_object.sqlite_object import SQLiteObject, get_sqlite_object

create_table_sql = """
CREATE TABLE IF NOT EXISTS tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def get_object(table) -> SQLiteObject:
    sqlite_object = SQLiteObject("test.db")
    sqlite_object.set_table(table)
    return sqlite_object


class TestSQLiteObject(unittest.TestCase):

    # add method to run before each test
    @classmethod
    def setUp(self):
        sqlite_object = get_object("tests")
        sqlite_object.execute(create_table_sql)
        sqlite_object.close()

    def test_get_sqlite_object(self):

        # get object one
        sqlite_object = get_object("tests")
        self.assertIsInstance(sqlite_object, SQLiteObject)

        # get the same object again
        same_sqlite_object = get_object("tests")

        # assert different objects
        self.assertNotEqual(sqlite_object, same_sqlite_object)

        sqlite_object.close()
        same_sqlite_object.close()

    def test_select_one(self):
        sqlite_object = get_object("tests")
        sqlite_object.insert({"title": "test"})
        result = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))
        self.assertEqual(result["title"], "test")
        sqlite_object.close()

    def test_select_one_simple(self):
        sqlite_object = get_object("tests")
        sqlite_object.insert({"title": "test"})
        result = sqlite_object.fetchone_simple(where={"title": "test"})
        self.assertEqual(result["title"], "test")
        sqlite_object.close()
    def test_insert(self):
        sqlite_object = get_object("tests")

        sqlite_object.delete(where="title = ?", placeholder_values=("test",))
        sqlite_object.insert({"title": "test"})
        result = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))

        self.assertEqual(result["title"], "test")
        sqlite_object.close()

    def test_delete(self):

        sqlite_object = get_object("tests")
        sqlite_object.insert({"title": "test"})
        sqlite_object.delete(where="title = ?", placeholder_values=("test",))
        result = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))
        self.assertIsNone(result)
        sqlite_object.close()

    def test_delete_simple(self):

        sqlite_object = get_object("tests")
        sqlite_object.insert({"title": "test"})
        sqlite_object.delete_simple(where={"title": "test"})
        result = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))
        self.assertIsNone(result)
        sqlite_object.close()

    def test_update(self):

        sqlite_object = get_object("tests")
        sqlite_object.insert(values={"title": "test"})
        sqlite_object.update(
            values={"title": "new test"},
            where="title = ?",
            placeholder_values=("test",),
        )

        result = sqlite_object.fetchone(
            where="title = ?", placeholder_values=("new test",)
        )
        self.assertEqual(result["title"], "new test")

        sqlite_object.delete(where="title = ?", placeholder_values=("new test",))
        sqlite_object.close()

    def test_update_simple(self):

        sqlite_object = get_object("tests")
        sqlite_object.insert(values={"title": "test"})
        sqlite_object.update_simple(
            values={"title": "new test"}, where={"title": "test"}
        )

        result = sqlite_object.fetchone(
            where="title = ?", placeholder_values=("new test",)
        )

        self.assertEqual(result["title"], "new test")

        sqlite_object.delete(where="title = ?", placeholder_values=("new test",))
        sqlite_object.close()

    def test_insert_id(self):
        sqlite_object = get_object("tests")
        sqlite_object.insert(values={"title": "test"})
        insert_id = sqlite_object.insert_id()
        self.assertTrue(insert_id > 0)

        sqlite_object.delete(where="title = ?", placeholder_values=("test",))
        sqlite_object.close()

    def test_rows_affected(self):
        sqlite_object = get_object("tests")
        sqlite_object.insert(values={"title": "test"})
        sqlite_object.delete(where="title = ?", placeholder_values=("test",))
        result = sqlite_object.rows_affected()
        self.assertTrue(result == 1)
        sqlite_object.close()

    def test_select_one_select_all_simple(self):
        sqlite_object = get_object("tests")
        sqlite_object.delete(
            where="title = ? OR title = ?",
            placeholder_values=(
                "test",
                "test2",
            ),
        )
        sqlite_object.insert(values={"title": "test"})
        sqlite_object.insert(values={"title": "test"})

        row = sqlite_object.fetchone_simple(where={"title": "test"})
        self.assertEqual(row["title"], "test")

        rows = sqlite_object.fetchall_simple(where={"title": "test"})

        self.assertTrue(len(rows) == 2)
        sqlite_object.close()

    def test_select_one_select_all(self):
        sqlite_object = get_object("tests")
        sqlite_object.delete(
            where="title = ? OR title= ?",
            placeholder_values=(
                "test",
                "test2",
            ),
        )
        sqlite_object.insert(values={"title": "test"})
        sqlite_object.insert(values={"title": "test2"})

        row = sqlite_object.fetchone(where="title = ?", placeholder_values=("test",))
        self.assertEqual(row["title"], "test")

        rows = sqlite_object.fetchall(
            where="title = ? OR title = ?",
            placeholder_values=(
                "test",
                "test2",
            ),
        )

        self.assertTrue(len(rows) == 2)
        sqlite_object.close()

    def test_replace(self):
        sqlite_object = get_object("tests")

        sqlite_object.insert(values={"title": "replace test"})
        sqlite_object.insert(values={"title": "replace test"})

        sqlite_object.replace(
            values={"title": "replace test updated"}, where={"title": "replace test"}
        )
        self.assertEqual(sqlite_object.rows_affected(), 2)

        rows = sqlite_object.fetchall_simple(where={"title": "replace test updated"})
        self.assertEqual(len(rows), 2)

        rows = sqlite_object.fetchall_simple(where={"title": "replace test"})
        self.assertEqual(len(rows), 0)

        sqlite_object.replace(
            values={"title": "replace test inserted"}, where={"title": "replace test"}
        )
        self.assertEqual(sqlite_object.rows_affected(), 1)

        rows = sqlite_object.fetchall_simple(where={"title": "replace test inserted"})
        self.assertEqual(len(rows), 1)

        sqlite_object.delete_simple(where={"title": "replace test updated"})
        sqlite_object.delete_simple(where={"title": "replace test inserted"})
        sqlite_object.close()

    def test_in_transaction_execute(self):

        sqlite_object = get_object("tests")

        def test_function():
            sqlite_object.insert(values={"title": "transaction test"})
            sqlite_object.insert(values={"title": "transaction test"})
            sqlite_object.insert(
                values={"unknown_column_causing_exception": "transaction test"}
            )

        try:
            self.assertRaises(
                Error, sqlite_object.in_transaction_execute(test_function)
            )
        except Error as e:
            # print(e)
            # 'table tests has no column named unknown_column_causing_exception'
            # Unknown column 'unknown_column_causing_exception' in 'field list'
            self.assertEqual(
                e.args[0],
                "table tests has no column named unknown_column_causing_exception",
            )

        num_rows = sqlite_object.get_num_rows({"title": "transaction test"}, "*")
        self.assertEqual(num_rows, 0)

        def test_function_working():
            sqlite_object.insert(values={"title": "transaction test"})
            sqlite_object.insert(values={"title": "transaction test"})
            sqlite_object.insert(values={"title": "transaction test"})

        sqlite_object.in_transaction_execute(test_function_working)
        num_rows = sqlite_object.get_num_rows({"title": "transaction test"})
        self.assertEqual(num_rows, 3)

        sqlite_object.delete_simple(where={"title": "transaction test"})

        sqlite_object.close()

    def test_get_num_rows(self):

        sqlite_object = get_object("tests")

        sqlite_object.insert(values={"title": "test"})
        sqlite_object.insert(values={"title": "test"})

        num_rows = sqlite_object.get_num_rows(where={"title": "test"})
        self.assertEqual(num_rows, 2)

        sqlite_object.delete_simple(where={"title": "test"})

        sqlite_object.close()

    def test_sql_query(self):

        query = SQLQuery().select("tests").where("title = ? OR title = ?").get_query()
        self.assertEqual(query, "SELECT * FROM tests WHERE title = ? OR title = ?")

        query = SQLQuery()
        query.select("tests")
        query.where("title = ? OR title = ?")
        query.order_by([("test", "DESC"), ("title", "ASC")])
        query.limit([30, 10])

        sql = query.get_query()
        self.assertEqual(
            sql,
            "SELECT * FROM tests WHERE title = ? OR title = ? ORDER BY test DESC, title ASC LIMIT 30, 10",
        )

        query = SQLQuery()
        sql = (
            query.select("tests")
            .where("title = ? OR title = ?")
            .order_by([("title", "ASC")])
            .limit([30, 10])
            .get_query()
        )

        self.assertEqual(
            sql,
            "SELECT * FROM tests WHERE title = ? OR title = ? ORDER BY title ASC LIMIT 30, 10",
        )

        


if __name__ == "__main__":
    unittest.main()
