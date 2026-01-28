import unittest
from app import create_app 

class BasicTestCase(unittest.TestCase): 
    
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_home_status_code(self):   
        response = self.client.get('/', follow_redirects=True)
        self.assertTrue(response.status_code in [200, 401])

if __name__ == '__main__':
    unittest.main()