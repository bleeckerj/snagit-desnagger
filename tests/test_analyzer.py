import os
import unittest
from src.analyzer import analyze_file
from io import StringIO
import sys

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_sample.bin'
        # Create a dummy file with some random data and a PNG signature
        with open(self.test_file, 'wb') as f:
            f.write(b'junk data...')
            f.write(b'\x89PNG\r\n\x1a\n') # PNG signature
            f.write(b'more junk...')
            f.write(b'\xff\xd8\xff') # JPEG signature

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_analyze_file(self):
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        analyze_file(self.test_file)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("Found PNG signature", output)
        self.assertIn("Found JPEG signature", output)

if __name__ == '__main__':
    unittest.main()
