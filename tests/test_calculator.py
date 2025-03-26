import unittest
import sys
import os

# Add parent directory to path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator import calculate_win_rate
from utils.card import validate_cards

class TestCalculator(unittest.TestCase):
    def test_pocket_pairs(self):
        """Test pocket pairs - Aces vs Kings"""
        num_players = 2
        hole_cards = [["AS", "AC"], ["KS", "KC"]]
        community_cards = []
        
        results = calculate_win_rate(num_players, hole_cards, community_cards)
        
        # Aces should have approximately 80-85% win rate against Kings
        self.assertGreater(results["Player 1"], 80)
        self.assertLess(results["Player 1"], 90)
        self.assertGreater(results["Player 2"], 10)
        self.assertLess(results["Player 2"], 20)
    
    def test_post_flop(self):
        """Test post-flop evaluation"""
        num_players = 3
        hole_cards = [["AH", "KD"], ["KS", "QC"], ["QS", "JC"]]
        community_cards = ["2C", "7D", "8S"]
        
        results = calculate_win_rate(num_players, hole_cards, community_cards)
        
        # Verify total percentages add up to approximately 100%
        total = sum(results.values())
        self.assertAlmostEqual(total, 100, delta=1)
        
        # Player 1 (AK) should have the highest win percentage
        self.assertGreater(results["Player 1"], results["Player 2"])
        self.assertGreater(results["Player 1"], results["Player 3"])
    
    def test_card_validation(self):
        """Test card validation"""
        # Valid cards
        valid_cards = ["AH", "KD", "QS", "JC", "TC"]
        self.assertTrue(validate_cards(valid_cards))
        
        # Invalid format
        invalid_cards = ["AH", "KD", "Q", "JC"]
        with self.assertRaises(ValueError):
            validate_cards(invalid_cards)
        
        # Invalid rank or suit
        invalid_cards = ["AH", "KD", "QX", "JC"]
        with self.assertRaises(ValueError):
            validate_cards(invalid_cards)
        
        # Duplicate cards
        duplicate_cards = ["AH", "KD", "AH", "JC"]
        with self.assertRaises(ValueError):
            validate_cards(duplicate_cards)

if __name__ == "__main__":
    unittest.main() 