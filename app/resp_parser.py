class RESPParser:
    def __init__(self):
        pass

    def parse(self, data):
        """
        Parse RESP protocol data.
        
        Args:
            data: bytes object containing RESP data
            
        Returns:
            Tuple of (parsed_data, bytes_consumed) or (None, 0) if incomplete
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes, not {}".format(type(data).__name__))
            
        if not data:
            return None, 0
            
        # Determine the type of message by first byte
        first_byte = data[0:1]
        
        if first_byte == b'+':
            return self._parse_simple_string(data)
        elif first_byte == b'-':
            return self._parse_error(data)
        elif first_byte == b':':
            return self._parse_integer(data)
        elif first_byte == b'$':
            return self._parse_bulk_string(data)
        elif first_byte == b'*':
            return self._parse_array(data)
        else:
            raise ValueError(f"Unsupported RESP type: {first_byte!r}")
            
    def _parse_simple_string(self, data):
        """Parse a simple string (+)."""
        end_idx = data.find(b'\r\n')
        if end_idx == -1:
            return None, 0
        
        parsed_data = data[1:end_idx].decode('utf-8')
        bytes_consumed = end_idx + 2
        return parsed_data, bytes_consumed
        
    def _parse_error(self, data):
        """Parse an error (-)."""
        end_idx = data.find(b'\r\n')
        if end_idx == -1:
            return None, 0
        
        parsed_data = data[1:end_idx].decode('utf-8')
        bytes_consumed = end_idx + 2
        return parsed_data, bytes_consumed
        
    def _parse_integer(self, data):
        """Parse an integer (:)."""
        end_idx = data.find(b'\r\n')
        if end_idx == -1:
            return None, 0
        
        parsed_data = int(data[1:end_idx])
        bytes_consumed = end_idx + 2
        return parsed_data, bytes_consumed
        
    def _parse_bulk_string(self, data):
        """Parse a bulk string ($)."""
        end_idx = data.find(b'\r\n')
        if end_idx == -1:
            return None, 0
        
        try:
            length = int(data[1:end_idx])
        except ValueError:
            raise ValueError(f"Invalid bulk string length: {data[1:end_idx]!r}")
            
        if length == -1:
            return None, end_idx + 2
        
        bulk_start = end_idx + 2
        bulk_end = bulk_start + length
        
        # Check if we have enough data
        if len(data) < bulk_end + 2:
            return None, 0
            
        # Check for proper termination with CRLF
        if data[bulk_end:bulk_end+2] != b'\r\n':
            raise ValueError("Bulk string not properly terminated with CRLF")
            
        parsed_data = data[bulk_start:bulk_end].decode('utf-8')
        bytes_consumed = bulk_end + 2
        return parsed_data, bytes_consumed
        
    def _parse_array(self, data):
        """Parse an array (*)."""
        end_idx = data.find(b'\r\n')
        if end_idx == -1:
            return None, 0
        
        try:
            num_elements = int(data[1:end_idx])
        except ValueError:
            raise ValueError(f"Invalid array length: {data[1:end_idx]!r}")
            
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
