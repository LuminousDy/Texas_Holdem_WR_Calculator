import itertools
import random

# Card constants
RANKS = '23456789TJQKA'
SUITS = 'SHDC'  # Spades, Hearts, Diamonds, Clubs

def create_deck(exclude_cards=None):
    """
    Create a standard 52-card deck, optionally excluding specific cards.
    
    Args:
        exclude_cards (list): List of card strings to exclude
    
    Returns:
        list: List of card strings representing a deck
    """
    if exclude_cards is None:
        exclude_cards = []
    
    deck = [r + s for r in RANKS for s in SUITS]
    return [card for card in deck if card not in exclude_cards]

def validate_cards(cards):
    """
    Validate that cards are in the correct format and no duplicates exist.
    
    Args:
        cards (list): List of card strings
    
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not all(len(card) == 2 for card in cards):
        raise ValueError("Cards must be in format 'RS' where R is rank and S is suit")
    
    if not all(card[0] in RANKS and card[1] in SUITS for card in cards):
        raise ValueError(f"Invalid card format. Rank must be one of {RANKS} and suit one of {SUITS}")
    
    if len(cards) != len(set(cards)):
        raise ValueError("Duplicate cards found")
    
    return True

def enumerate_remaining_cards(used_cards, num_cards):
    """
    Generate all possible combinations of remaining cards.
    
    Args:
        used_cards (list): List of card strings already in use
        num_cards (int): Number of cards to draw
    
    Returns:
        list: List of card combinations
    """
    deck = create_deck(used_cards)
    return list(itertools.combinations(deck, num_cards))

def deal_random_cards(used_cards, num_cards):
    """
    Deal random cards from the remaining deck.
    
    Args:
        used_cards (list): List of card strings already in use
        num_cards (int): Number of cards to deal
    
    Returns:
        list: Randomly dealt cards
    """
    deck = create_deck(used_cards)
    if len(deck) < num_cards:
        raise ValueError(f"Not enough cards left in deck to deal {num_cards} cards")
    
    return random.sample(deck, num_cards)

def get_mirrored_cards(cards):
    """
    Generate mirrored cards by swapping suits in a systematic way.
    This is used for variance reduction in Monte Carlo simulations through antithetic variates.
    
    Args:
        cards (list): List of card strings to mirror
        
    Returns:
        list: Mirrored versions of the input cards
    """
    # Map for suit mirroring: Spades<->Hearts, Diamonds<->Clubs
    suit_mirror = {'S': 'H', 'H': 'S', 'D': 'C', 'C': 'D'}
    
    mirrored_cards = []
    for card in cards:
        rank = card[0]
        suit = card[1]
        mirrored_suit = suit_mirror[suit]
        mirrored_cards.append(rank + mirrored_suit)
    
    return mirrored_cards
