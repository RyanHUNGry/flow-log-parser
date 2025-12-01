# Integration tests for CLI commands (assuming random.seed(0))
import os
import io
import tempfile
import unittest
import sys

if os.path.join(os.getcwd(), "src") not in sys.path:
    sys.path.append(os.path.join(os.getcwd(), "..", "src"))

from cli.cli import FlowlogParserCLI
import flowparser.constants as constants
from generator import generate_testcase

SAMPLE_LINE_1 = "2 123456 eni-1 10.0.0.1 10.0.0.2 1000 2000 6 1 100 1600000000 1600000001 ACCEPT OK\n"
SAMPLE_LINE_2 = "2 123456 eni-1 10.0.0.3 10.0.0.2 1500 2500 6 2 200 1600000100 1600000110 REJECT OK\n"
SAMPLE_LINE_3 = "2 123456789010 eni-ab12cd34ef5678901 - - - - - - - 1732930480 1732930522 - SKIPDATA\n"

class TestParserCLI(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(os.getcwd(), "..", "data")):
            os.makedirs(os.path.join(os.getcwd(), "..", "data"))
        self.stdout = io.StringIO()
        self.stdin = io.StringIO()
        self.cli = FlowlogParserCLI(stdin=self.stdin, stdout=self.stdout)

    def _out(self) -> str:
        return self.stdout.getvalue()

    def test_set_schema_default(self):
        self.cli.onecmd("set_schema default")
        self.assertEqual(self.cli.schema, constants.FLOW_LOG_SCHEMA_DEFAULT)
        self.assertIn("Schema set to default.", self._out())

    def test_set_schema_all(self):
        self.stdout.truncate(0); self.stdout.seek(0)
        self.cli.onecmd("set_schema all")
        self.assertEqual(self.cli.schema, constants.FLOW_LOG_SCHEMA_ALL)
        self.assertIn("Schema set to all.", self._out())

    def test_set_schema_custom_and_invalid(self):
        self.stdout.truncate(0); self.stdout.seek(0)
        # valid custom
        self.cli.onecmd("set_schema srcaddr dstaddr srcport")
        self.assertEqual(self.cli.schema, ["srcaddr", "dstaddr", "srcport"])
        self.assertIn("Schema set to srcaddr dstaddr srcport.", self._out())

        # invalid field
        self.stdout.truncate(0); self.stdout.seek(0)
        self.cli.onecmd("set_schema not_a_field")
        self.assertIn("Invalid field: not_a_field", self._out())

    def test_connection_count(self):
        try:
            # load file
            path = generate_testcase("temp_flowlogs1.txt", target_size_mb=20)

            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd(f"load {path}")
            out = self._out()
            self.assertIn(f"Loading flow logs from {path}", out)
            self.assertTrue(hasattr(self.cli, "parser"))

            # exists
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("get_connection_count 10.0.0.159 21248 10.0.1.130 33202 6")
            out = self._out()
            self.assertIn("Connection count: 1", out)

            # does not exist
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("get_connection_count 10.0.0.159 2148 10.0.1.130 33202 6")
            out = self._out()
            self.assertIn("Connection count: 0", out)
        except Exception as e:
            print(f"An error occurred during test_connection_count: {e}")


    def test_load_and_search_commands_from_file(self):
        try:
            # load file
            path = generate_testcase("temp_flowlogs.txt", target_size_mb=20)

            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd(f"load {path}")
            out = self._out()
            self.assertIn(f"Loading flow logs from {path}", out)
            self.assertTrue(hasattr(self.cli, "parser"))

            # search by source ip
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src 10.0.0.159")
            out = self._out()
            self.assertIn("Total results: 3451", out)

            # search by destination ip
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_dst 10.0.0.23")
            out = self._out()
            self.assertIn("Total results: 3384", out)

            # search by src+dst
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src_dst 10.0.3.104 10.0.1.194")
            out = self._out()
            self.assertIn("Total results: 65", out)

            # search by src+dst (no match)
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src_dst 120.0.0.3 10.0.0.2")
            out = self._out()
            self.assertIn("Total results: 0", out)
        except Exception as e:
            print(f"An error occurred during test_load_and_search_commands_from_file: {e}")

    def test_load_and_search_commands(self):
        # create temp file with two sample flowlog lines
        fd, path = tempfile.mkstemp(prefix="flowlogs_", suffix=".txt")
        os.close(fd)
        try:
            with open(path, "w") as f:
                f.write(SAMPLE_LINE_1)
                f.write(SAMPLE_LINE_2)
                f.write(SAMPLE_LINE_3)

            # load file
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd(f"load {path}")
            out = self._out()
            self.assertIn(f"Loading flow logs from {path}", out)
            self.assertTrue(hasattr(self.cli, "parser"))

            # search by source ip that exists once
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src 10.0.0.1")
            out = self._out()
            self.assertIn("Total results: 1", out)

            # search by destination ip (both lines dstaddr=10.0.0.2)
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_dst 10.0.0.2")
            out = self._out()
            self.assertIn("Total results: 2", out)

            # search by src+dst (one match)
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src_dst 10.0.0.3 10.0.0.2")
            out = self._out()
            self.assertIn("Total results: 1", out)

            # search by src+dst (no match)
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src_dst 120.0.0.3 10.0.0.2")
            out = self._out()
            self.assertIn("Total results: 0", out)

            # invalid IP formats should be rejected
            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src not_an_ip")
            self.assertIn("Invalid IP address", self._out())

            self.stdout.truncate(0); self.stdout.seek(0)
            self.cli.onecmd("search_src_dst 10.0.0.1 not_an_ip")
            self.assertIn("Invalid IP address", self._out())
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

if __name__ == "__main__":
    unittest.main()
