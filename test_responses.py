from app import app
import unittest


class FlaskTestCase(unittest.TestCase):
    # Make sure that the flask was set up correctly
    def test_user_registration(self):
        tester = app.test_client(self)
        response = tester.get('/user-registration/', content_type='html/text/json')
        self.assertEqual(response.status_code, 200)

    def test_add_product(self):
        tester = app.test_client(self)
        response = tester.get('/add-product/', content_type='html/text/json')
        self.assertEqual(response.status_code, 200)

    def test_products(self):
        test = app.test_client(self)
        response = test.get('/get-products/', content_type='html/text/json')
        status = response.status_code
        self.assertEqual(status, 200)

if __name__ == '__main__':
    unittest.main()
