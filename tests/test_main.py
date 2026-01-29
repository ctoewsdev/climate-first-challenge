"""
Tests for main entry point (pipeline orchestration, error handling).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import unittest
from io import StringIO
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    @patch("main.run_pipeline")
    def test_main_success(self, mock_run_pipeline):
        """Test that main calls run_pipeline successfully."""
        mock_run_pipeline.return_value = None
        main()
        mock_run_pipeline.assert_called_once()

    @patch("main.run_pipeline")
    def test_main_prints_expected_on_success(self, mock_run_pipeline):
        """Success run prints: clear msg, running, congratulations."""
        mock_run_pipeline.return_value = None
        stdout_capture = StringIO()
        with patch("sys.stdout", stdout_capture):
            main(clear=True)
        out = stdout_capture.getvalue()
        self.assertIn("Clearing output directory...", out)
        self.assertIn("Running pipeline...", out)
        self.assertIn("Congratulations! All layers complete. Watch out for drop bears.", out)

    @patch("main.run_pipeline")
    def test_main_no_clear_skips_clearing_message(self, mock_run_pipeline):
        """With clear=False, no 'Clearing output directory...'; still running + congratulations."""
        mock_run_pipeline.return_value = None
        stdout_capture = StringIO()
        with patch("sys.stdout", stdout_capture):
            main(clear=False)
        out = stdout_capture.getvalue()
        self.assertNotIn("Clearing output directory...", out)
        self.assertIn("Running pipeline...", out)
        self.assertIn("Congratulations! All layers complete. Watch out for drop bears.", out)

    @patch("main.run_pipeline")
    @patch("sys.exit")
    def test_main_handles_exception(self, mock_exit, mock_run_pipeline):
        """Test that main handles exceptions properly."""
        mock_run_pipeline.side_effect = Exception("Test error message")
        stderr_capture = StringIO()
        with patch("sys.stderr", stderr_capture):
            main()
        self.assertIn("Error: Test error message", stderr_capture.getvalue())
        mock_exit.assert_called_once_with(1)

    @patch("main.run_pipeline")
    @patch("sys.exit")
    def test_main_handles_specific_exception(self, mock_exit, mock_run_pipeline):
        """Test that main handles specific exceptions."""
        mock_run_pipeline.side_effect = ValueError("Invalid input")
        stderr_capture = StringIO()
        with patch("sys.stderr", stderr_capture):
            main()
        self.assertIn("Invalid input", stderr_capture.getvalue())
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
