import random
from utils.card import deal_random_cards
from evaluator import compare_hands
from utils.parallel import parallel_execute, get_computation_device
import multiprocessing

def run_simulation_batch(batch_size, num_players, hole_cards, community_cards, all_cards):
    """
    Run a batch of simulations for parallel processing.
    
    Args:
        batch_size (int): Number of simulations to run in this batch
        num_players (int): Number of players
        hole_cards (list): List of hole card pairs for each player
        community_cards (list): List of community cards
        all_cards (list): All known cards for deck exclusion
        
    Returns:
        tuple: (wins, ties) counts for each player
    """
    wins = [0] * num_players
    ties = [0] * num_players
    
    for _ in range(batch_size):
        # Deal remaining community cards to complete the board
        remaining_cards = 5 - len(community_cards)
        if remaining_cards > 0:
            simulated_board = community_cards + deal_random_cards(all_cards, remaining_cards)
        else:
            simulated_board = community_cards
        
        # Compare hands and find winner(s)
        winners = compare_hands(hole_cards, simulated_board)
        
        # Update counters
        if len(winners) == 1:
            wins[winners[0]] += 1
        else:
            for winner in winners:
                ties[winner] += 1
    
    return (wins, ties)

def monte_carlo_simulation(num_players, hole_cards, community_cards=None, iterations=10000):
    """
    Perform Monte Carlo simulation to estimate win rates.
    
    Args:
        num_players (int): Number of players (2-9)
        hole_cards (list): List of hole card pairs for each player
        community_cards (list, optional): List of community cards (0-5)
        iterations (int, optional): Number of simulations to run
    
    Returns:
        dict: Win percentages for each player
    """
    if community_cards is None:
        community_cards = []
    
    # Validate inputs
    if num_players < 2 or num_players > 9:
        raise ValueError("Number of players must be between 2 and 9")
    
    if len(hole_cards) != num_players:
        raise ValueError("Number of hole card pairs must match number of players")
    
    if len(community_cards) > 5:
        raise ValueError("Maximum of 5 community cards allowed")
    
    # Flatten all known cards for deck exclusion
    all_cards = [card for hand in hole_cards for card in hand] + community_cards
    
    # Adaptive iteration count
    if num_players <= 3:
        iterations = max(iterations, 120000)
    elif num_players <= 6:
        iterations = max(iterations, 100000)
    else:
        iterations = max(iterations, 80000)
    
    # Check for GPU acceleration
    device = get_computation_device()
    if device == 'gpu':
        print("Using GPU acceleration for Monte Carlo simulation")
        # TODO: Implement GPU acceleration if available
        # For now, fall back to CPU parallelization
    
    # Set up parallel execution
    num_cores = multiprocessing.cpu_count()
    batch_size = iterations // num_cores
    remaining = iterations % num_cores
    
    # Prepare batch arguments
    batch_args = []
    for i in range(num_cores):
        # Add one extra iteration to the first 'remaining' batches
        current_batch_size = batch_size + (1 if i < remaining else 0)
        batch_args.append((current_batch_size, num_players, hole_cards, community_cards, all_cards))
    
    # Run batches in parallel
    batch_results = parallel_execute(run_simulation_batch, batch_args)
    
    # Combine results
    total_wins = [0] * num_players
    total_ties = [0] * num_players
    
    for wins, ties in batch_results:
        for i in range(num_players):
            total_wins[i] += wins[i]
            total_ties[i] += ties[i]
    
    # Calculate win percentages
    results = {}
    for i in range(num_players):
        # Calculate win percentage, handling potential division by zero
        if total_ties[i] > 0:
            tie_contribution = total_ties[i] / sum(1 for t in total_ties if t > 0)
        else:
            tie_contribution = 0
            
        win_percentage = (total_wins[i] + tie_contribution) / iterations * 100
        results[f"Player {i+1}"] = round(win_percentage, 2)
    
    return results
