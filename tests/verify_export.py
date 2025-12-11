
import unittest
from unittest.mock import patch
import os
import sys
import csv

# Ensure we import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from terminal_vault.cli.main import main
from terminal_vault.core.vault import Vault

class TestExportCommand(unittest.TestCase):
    def setUp(self):
        self.test_prefix = 'test_export_cmd'
        self.vault_file = f'{self.test_prefix}.json'
        self.csv_file = f'{self.test_prefix}.csv'
        self.dat_file = f'{self.test_prefix}.dat'
        
        # Cleanup
        self.cleanup()
        
        # Mock Config
        self.config_patcher = patch('terminal_vault.cli.main.Config')
        self.mock_config_cls = self.config_patcher.start()
        self.mock_config = self.mock_config_cls.return_value
        
        def get_conf(section, key):
            if key == 'vault_file': return self.vault_file
            if key == 'log_file': return 'test_vault.log'
            return 'value'
            
        self.mock_config.get.side_effect = get_conf

    def tearDown(self):
        self.config_patcher.stop()
        self.cleanup()

    def cleanup(self):
        for f in [self.vault_file, self.csv_file, self.dat_file]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

    @patch('builtins.print')
    @patch('builtins.input')
    @patch('terminal_vault.cli.main.get_masked_input')
    def test_export_flow(self, mock_getpass, mock_input, mock_print):
        # 1. INIT
        mock_input.side_effect = ['admin'] 
        mock_getpass.side_effect = ['password123', 'password123']
        with patch.object(sys, 'argv', ['vault', 'init']):
            main()
            
        self.assertTrue(os.path.exists(self.vault_file))
        # Verify CSV does NOT exist yet
        self.assertFalse(os.path.exists(self.csv_file), "CSV should not persist after init")

        # 2. ADD ENTRY
        mock_input.side_effect = ['admin', 'Secret Note Content']
        mock_getpass.side_effect = ['password123']
        with patch.object(sys, 'argv', ['vault', 'add', '--title', 'Test Note', '--tags', 'test']):
            main()
            
        # Verify CSV still does NOT exist
        self.assertFalse(os.path.exists(self.csv_file), "CSV should not persist after add")

        # 3. EXPORT
        mock_input.side_effect = ['admin'] # Auth
        mock_getpass.side_effect = ['password123']
        with patch.object(sys, 'argv', ['vault', 'export']):
            main()
            
        # Verify CSV DOES exist now
        self.assertTrue(os.path.exists(self.csv_file), "CSV should exist after export")
        
        # Verify content
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['title'], 'Test Note')
            self.assertEqual(rows[0]['note'], 'Secret Note Content')

if __name__ == '__main__':
    unittest.main()
