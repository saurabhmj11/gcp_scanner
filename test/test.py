import unittest
from scanner import GCScanner

class TestGCScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = GCScanner()

    def test_compute_engine(self):
        # Test if compute engine is running
        result = self.scanner.check_compute_engine()
        self.assertTrue(result)

    def test_storage_buckets(self):
        # Test if all storage buckets are public
        result = self.scanner.check_storage_buckets()
        self.assertFalse(result)

    def test_cloud_sql(self):
        # Test if Cloud SQL instances are using SSL
        result = self.scanner.check_cloud_sql()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
