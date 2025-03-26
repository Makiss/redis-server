import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RESPParserError(Exception):
    """Base class for RESP parser errors."""
    pass


class RESPInvalidFormatError(RESPParserError):
    """Raised when the RESP data format is invalid."""
    pass


class RESPParser:
    """Parser for Redis Serialization Protocol (RESP)."""
    
    def __init__(self):
        self._type_parsers = {
            b'+': self._parse_simple_string,
            b'-': self._parse_error,
            b':': self._parse_integer,
            b'$': self._parse_bulk_string,
            b'*': self._parse_array
        }

    def parse(self, data):
        """
        Parse RESP protocol data.
        
        Args:
            data: bytes object containing RESP data
            
        Returns:
            Tuple of (parsed_data, bytes_consumed) or (None, 0) if incomplete
        """
        logger.debug(f"Parsing data: {data}")
        if not isinstance(data, bytes):
            raise TypeError(f"Data must be bytes, not {type(data).__name__}")
            
        if not data:
            return None, 0
            
        # Get the parser for the RESP type marker
        first_byte = data[0:1]
        parser = self._type_parsers.get(first_byte)
        
        if parser:
            return parser(data)
        else:
            raise RESPInvalidFormatError(f"Unsupported RESP type: {first_byte!r}")
    
    def _find_line_end(self, data):
        """Find the end of a RESP line (CRLF)."""
        end_idx = data.find(b'\r\n')
        return end_idx
    
    def _parse_line(self, data, transform_func=None):
        """
        Parse a simple RESP line ending with CRLF.
        
        Args:
            data: bytes data starting with type marker
            transform_func: optional function to transform the parsed data
            
        Returns:
            Tuple of (parsed_data, bytes_consumed) or (None, 0) if incomplete
        """
        end_idx = self._find_line_end(data)
        if end_idx == -1:
            return None, 0
        
        content = data[1:end_idx]
        bytes_consumed = end_idx + 2  # Include CRLF
        
        if transform_func:
            try:
                parsed_data = transform_func(content)
            except ValueError as e:
                raise RESPInvalidFormatError(f"Invalid format: {str(e)}")
        else:
            parsed_data = content
            
        return parsed_data, bytes_consumed
            
    def _parse_simple_string(self, data):
        """Parse a simple string (+)."""
        return self._parse_line(data, lambda x: x.decode('utf-8'))
        
    def _parse_error(self, data):
        """Parse an error (-)."""
        return self._parse_line(data, lambda x: x.decode('utf-8'))
        
    def _parse_integer(self, data):
        """Parse an integer (:)."""
        return self._parse_line(data, lambda x: int(x))
        
    def _parse_bulk_string(self, data):
        """Parse a bulk string ($)."""
        end_idx = self._find_line_end(data)
        if end_idx == -1:
            return None, 0
        
        try:
            length = int(data[1:end_idx])
        except ValueError:
            raise RESPInvalidFormatError(f"Invalid bulk string length: {data[1:end_idx]!r}")
            
        if length == -1:
            return None, end_idx + 2
        
        bulk_start = end_idx + 2
        bulk_end = bulk_start + length
        
        # Check if we have enough data
        if len(data) < bulk_end + 2:
            return None, 0
            
        # Check for proper termination with CRLF
        if data[bulk_end:bulk_end+2] != b'\r\n':
            raise RESPInvalidFormatError("Bulk string not properly terminated with CRLF")
            
        parsed_data = data[bulk_start:bulk_end].decode('utf-8')
        bytes_consumed = bulk_end + 2
        return parsed_data, bytes_consumed
        
    def _parse_array(self, data):
        """Parse an array (*)."""
        end_idx = self._find_line_end(data)
        if end_idx == -1:
            return None, 0
        
        try:
            num_elements = int(data[1:end_idx])
        except ValueError:
            raise RESPInvalidFormatError(f"Invalid array length: {data[1:end_idx]!r}")
            
        if num_elements == -1:
            return None, end_idx + 2
        
        elements = []
        bytes_consumed = end_idx + 2
        
        for _ in range(num_elements):
            if bytes_consumed >= len(data):
                return None, 0
                
            element, consumed = self.parse(data[bytes_consumed:])
            if element is None and consumed == 0:
                return None, 0
                
            elements.append(element)
            bytes_consumed += consumed

        return elements, bytes_consumed