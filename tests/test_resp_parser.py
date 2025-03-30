import unittest

from app.resp_parser import RESPParser, RESPInvalidFormatError


class TestRESPParser(unittest.TestCase):
    def setUp(self):
        self.parser = RESPParser()

    # Simple String Tests
    def test_partial_simple_string(self):
        data = b"+OK"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_simple_string(self):
        data = b"+OK\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (b"OK", 5))

    # Error Message Tests
    def test_partial_error_message(self):
        data = b"-ERROR"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_error_message(self):
        data = b"-ERROR\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (b"ERROR", 8))

    # Integer Tests
    def test_partial_integer(self):
        data = b":100"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_integer(self):
        data = b":1000\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (b"1000", 7))

    # Bulk String Tests
    def test_partial_bulk_string(self):
        data = b"$6\r\nfoob"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_bulk_string(self):
        data = b"$6\r\nfoobar\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (b"foobar", 12))

    def test_null_bulk_string(self):
        data = b"$-1\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 5))

    # Array Tests
    def test_partial_array(self):
        data = b"*2\r\n$3\r\nfoo"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))

    def test_complete_array(self):
        data = b"*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, ([b"foo", b"bar"], 22))

    def test_null_array(self):
        data = b"*-1\r\n"
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 5))
    
    # Error Handling Tests
    def test_type_error(self):
        with self.assertRaises(TypeError):
            self.parser.parse("not bytes")
            
    def test_unsupported_type(self):
        data = b"?invalid\r\n"
        with self.assertRaises(RESPInvalidFormatError):
            self.parser.parse(data)
    
    def test_empty_data(self):
        data = b""
        result = self.parser.parse(data)
        self.assertEqual(result, (None, 0))


if __name__ == "__main__":
    unittest.main()