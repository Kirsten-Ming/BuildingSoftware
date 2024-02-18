import unittest
from analysis.py import Analysis

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations for the tests
        pass

    def test_load_data(self):
        # Test the load_data method
        analysis_obj = Analysis('config.yml')
        analysis_obj.load_data()

        # Assert that the DataFrame is not empty after loading data
        self.assertFalse(analysis_obj.df.empty, "DataFrame should not be empty after loading data")

    def test_compute_analysis(self):
        # Test the compute_analysis method
        analysis_obj = Analysis('config.yml')
        analysis_obj.load_data()
        result = analysis_obj.compute_analysis()

        # Assert that the result is a pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame, "compute_analysis should return a pandas DataFrame")

    def test_notification(self):
        # Test the notify_done method
        analysis_obj = Analysis('config.yml')

        # Capture the standard output to check if the notification is printed
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            analysis_obj.notify_done('Test notification message')

            # Assert that the notification message is printed
            self.assertIn('Spotify Analysis Completed', mock_stdout.getvalue(), "Notification message not printed")

if __name__ == '__main__':
    unittest.main()
