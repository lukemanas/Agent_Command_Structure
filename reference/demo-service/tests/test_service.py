"""Stdlib-only tests for demo-service. Run with:
    python3 -m unittest discover demo-service/tests
"""
import os
import sys
import unittest

# allow `import service` from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from service import handle  # noqa: E402


class TestHealth(unittest.TestCase):
    def test_health_returns_200_ok(self):
        status, body = handle("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, "ok")

    def test_unknown_returns_404(self):
        status, body = handle("/missing-path")
        self.assertEqual(status, 404)

    def test_hello_returns_200_hello_world(self):
        status, body = handle("/hello")
        self.assertEqual(status, 200)
        self.assertEqual(body, "hello world")


if __name__ == "__main__":
    unittest.main()
