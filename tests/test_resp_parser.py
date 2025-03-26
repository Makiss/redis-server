import unittest

from app.resp_parser import RESPParser


class TestRESPParser(unittest.TestCase):
    def setUp(self):
        self.parser = RESPParser()

    def test_partial_simple_string(self):
        data = b"+OK"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_simple_string(self):
        data = b"+OK\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, ("OK", 5))

    def test_partial_error_message(self):
        data = b"-ERROR"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_error_message(self):
        data = b"-ERROR\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, ("ERROR", 8))

    def test_partial_integer(self):
        data = b":100"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_integer(self):
        data = b":1000\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (1000, 7))

    def test_partial_bulk_string(self):
        data = b"$6\r\nfoob"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_bulk_string(self):
        data = b"$6\r\nfoobar\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, ("foobar", 12))

    def test_null_bulk_string(self):
        data = b"$-1\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 5))

    def test_partial_array(self):
        data = b"*2\r\n$3\r\nfoo"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_array(self):
        data = b"*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (["foo", "bar"], 22))

    def test_null_array(self):
        data = b"*-1\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 5))
        
    def test_type_error(self):
        with self.assertRaises(TypeError):
            self.parser.parse("not bytes")


if __name__ == "__main__":
    unittest.main()
