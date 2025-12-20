import unittest
import sys
import os
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import main, load_page_module, get_main_text

class TestApp(unittest.TestCase):
    """Test cases for the main application"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_get_main_text(self):
        """Test text translation function"""
        # Test English
        text = get_main_text("app_title", "en")
        self.assertEqual(text, "🍽️ Restaurant Kitchen Inventory")
        
        # Test Spanish
        text = get_main_text("app_title", "es")
        self.assertEqual(text, "🍽️ Inventario de Cocina de Restaurante")
        
        # Test fallback
        text = get_main_text("nonexistent_key", "en")
        self.assertEqual(text, "nonexistent_key")
    
    def test_load_page_module(self):
        """Test page module loading"""
        # Test with valid page
        module = load_page_module("1_ProductDatabase")
        self.assertIsNotNone(module)
        
        # Test with invalid page
        module = load_page_module("nonexistent_page")
        self.assertIsNone(module)
    
    def test_main_function_exists(self):
        """Test that main function exists"""
        # This is a basic test to ensure the main function can be called
        # In a real test, we'd mock Streamlit components
        try:
            # Just test that the function exists and doesn't crash
            self.assertTrue(callable(main))
        except Exception as e:
            self.fail(f"Main function should exist: {e}")

if __name__ == '__main__':
    unittest.main() 