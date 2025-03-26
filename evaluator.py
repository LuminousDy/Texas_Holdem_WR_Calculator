from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

def rank_to_int(rank):
    """
    Convert rank string to integer value.
    
    Args:
        rank (str): Card rank as string ('2'-'9', 'T', 'J', 'Q', 'K', 'A')
    
    Returns:
        int: Integer representation of the rank
    """
    if rank.isdigit():
        return int(rank)
    rank_map = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    return rank_map[rank]

def suit_to_int(suit):
    """
    Convert suit string to integer value.
    
    Args:
        suit (str): Card suit as string ('S', 'H', 'D', 'C')
    
    Returns:
        int: Integer representation of the suit
    """
    suit_map = {'S': 1, 'H': 2, 'D': 4, 'C': 8}
    return suit_map[suit]

def evaluate_hand(hole_cards, community_cards):
    """
    Evaluate the strength of a poker hand.
    
    Args:
        hole_cards (list): List of 2 card strings (e.g., ["AH", "KD"])
        community_cards (list): List of community card strings (up to 5)
    
    Returns:
        int: Hand strength score
    """
    # Convert card format and create Card objects with proper integer values
    hole = [Card(suit=suit_to_int(card[1]), rank=rank_to_int(card[0])) for card in hole_cards]
    community = [Card(suit=suit_to_int(card[1]), rank=rank_to_int(card[0])) for card in community_cards]
    
    score = HandEvaluator.eval_hand(hole, community)
    return score

def compare_hands(hands, community_cards):
    """
    Compare multiple hands and determine the winner(s).
    
    Args:
        hands (list): List of hole card pairs (e.g., [["AH", "KD"], ["QS", "JC"]])
        community_cards (list): List of community card strings (up to 5)
    
    Returns:
        list: Indices of winning hands (multiple in case of a tie)
    """
    scores = [evaluate_hand(hand, community_cards) for hand in hands]
    max_score = max(scores)
    winners = [i for i, score in enumerate(scores) if score == max_score]
    return winners
