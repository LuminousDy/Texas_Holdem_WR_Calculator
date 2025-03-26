import unittest
import sys
import os

# Add parent directory to path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluator import evaluate_hand, compare_hands

class TestEvaluator(unittest.TestCase):
    def test_hand_evaluation(self):
        """Test hand evaluation scores"""
        # Royal flush
        royal_flush = ["TS", "JS", "QS", "KS", "AS"]
        royal_flush_score = evaluate_hand(royal_flush[:2], royal_flush[2:])
        
        # Straight flush
        straight_flush = ["9H", "TH", "JH", "QH", "KH"]
        straight_flush_score = evaluate_hand(straight_flush[:2], straight_flush[2:])
        
        # Four of a kind
        four_kind = ["AS", "AC", "AD", "AH", "KS"]
        four_kind_score = evaluate_hand(four_kind[:2], four_kind[2:])
        
        # Full house
        full_house = ["KS", "KC", "KD", "JH", "JS"]
        full_house_score = evaluate_hand(full_house[:2], full_house[2:])
        
        # Flush
        flush = ["2S", "5S", "7S", "JS", "AS"]
        flush_score = evaluate_hand(flush[:2], flush[2:])
        
        # Straight
        straight = ["9H", "TD", "JC", "QS", "KH"]
        straight_score = evaluate_hand(straight[:2], straight[2:])
        
        # Hand ranking (higher score is better)
        self.assertGreater(royal_flush_score, straight_flush_score)
        self.assertGreater(straight_flush_score, four_kind_score)
        self.assertGreater(four_kind_score, full_house_score)
        self.assertGreater(full_house_score, flush_score)
        self.assertGreater(flush_score, straight_score)
    
    def test_compare_hands(self):
        """Test comparing multiple hands"""
        # Test case 1: Clear winner
        hole_cards = [
            ["AH", "KH"],  # Player 1: Ace-King of Hearts
            ["QS", "JD"],  # Player 2: Queen-Jack offsuit
            ["TH", "9H"]   # Player 3: Ten-Nine of Hearts
        ]
        community_cards = ["2H", "3H", "4H", "5C", "7D"]
        # Player 1 has a flush, others have high card
        winners = compare_hands(hole_cards, community_cards)
        self.assertEqual(winners, [0])
        
        # Test case 2: Tie
        hole_cards = [
            ["AH", "KD"],  # Player 1: Ace-King offsuit
            ["AS", "KH"],  # Player 2: Ace-King offsuit
            ["AC", "KS"]   # Player 3: Ace-King offsuit
        ]
        community_cards = ["2H", "3H", "4H", "5C", "7D"]
        # All players have Ace-King high
        winners = compare_hands(hole_cards, community_cards)
        self.assertEqual(len(winners), 3)  # All three players tie

if __name__ == "__main__":
    unittest.main() 