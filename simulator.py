import random
from utils.card import deal_random_cards, get_mirrored_cards
from evaluator import compare_hands
from utils.parallel import parallel_execute, get_computation_device
import multiprocessing
import time
import numpy as np

def run_simulation_batch(batch_size, num_players, hole_cards, community_cards, all_cards, use_antithetic=True):
    """
    Run a batch of simulations for parallel processing.
    
    Args:
        batch_size (int): Number of simulations to run in this batch
        num_players (int): Number of players
        hole_cards (list): List of hole card pairs for each player
        community_cards (list): List of community cards
        all_cards (list): All known cards for deck exclusion
        use_antithetic (bool): Whether to use antithetic variates for variance reduction
        
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
            # Distribute win equally among tied players
            win_value = 1.0 / len(winners) 
            for winner in winners:
                ties[winner] += win_value
                
        # If using antithetic variates, run a mirrored simulation
        if use_antithetic and remaining_cards > 0:
            # Get mirrored community cards for variance reduction
            mirrored_board = community_cards + get_mirrored_cards(simulated_board[len(community_cards):])
            
            # Compare hands with mirrored board
            mirrored_winners = compare_hands(hole_cards, mirrored_board)
            
            # Update counters for mirrored simulation
            if len(mirrored_winners) == 1:
                wins[mirrored_winners[0]] += 1
            else:
                # Distribute win equally among tied players
                win_value = 1.0 / len(mirrored_winners)
                for winner in mirrored_winners:
                    ties[winner] += win_value
    
    return (wins, ties)

def check_convergence(win_rates, history, threshold=0.1):
    """
    Check if win rates have converged within threshold.
    
    Args:
        win_rates (list): Current win rates for each player
        history (list): History of win rates
        threshold (float): Convergence threshold
        
    Returns:
        bool: True if converged, False otherwise
    """
    if len(history) < 3:  # Need at least 3 checkpoints to assess convergence
        return False
        
    # Calculate average change over last 3 checkpoints
    diffs = []
    for i in range(1, min(4, len(history))):
        prev_rates = history[-i]
        max_diff = max(abs(r1 - r2) for r1, r2 in zip(win_rates, prev_rates))
        diffs.append(max_diff)
    
    avg_diff = sum(diffs) / len(diffs)
    return avg_diff < threshold

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
    
    # Get maximum available CPU cores
    num_cores = multiprocessing.cpu_count()
    
    # Use antithetic variates for variance reduction
    use_antithetic = True
    
    # If using antithetic variates, we can reduce the number of iterations
    if use_antithetic:
        iterations = int(iterations * 0.6)  # Each iteration produces 2 samples
    
    # Set up parallel execution
    batch_size = iterations // num_cores
    remaining = iterations % num_cores
    
    # Prepare batch arguments
    batch_args = []
    for i in range(num_cores):
        # Add one extra iteration to the first 'remaining' batches
        current_batch_size = batch_size + (1 if i < remaining else 0)
        batch_args.append((current_batch_size, num_players, hole_cards, community_cards, all_cards, use_antithetic))
    
    # For early termination based on convergence
    win_rate_history = []
    convergence_reached = False
    convergence_checks = 10  # Number of checkpoints to check convergence
    iterations_per_check = max(iterations // convergence_checks, 1000)
    
    # Track simulations completed
    simulations_completed = 0
    
    # Process simulation batches in chunks with convergence checks
    total_wins = [0] * num_players
    total_ties = [0] * num_players
    
    # Start timer
    start_time = time.time()
    
    # Break iterations into chunks for convergence checks
    while simulations_completed < iterations and not convergence_reached:
        # Calculate remaining simulations
        remaining_sims = iterations - simulations_completed
        chunk_size = min(iterations_per_check, remaining_sims)
        
        # Setup batch arguments for this chunk
        chunk_batch_size = chunk_size // num_cores
        chunk_remaining = chunk_size % num_cores
        
        chunk_batch_args = []
        for i in range(num_cores):
            # Add one extra iteration to the first 'chunk_remaining' batches
            current_batch_size = chunk_batch_size + (1 if i < chunk_remaining else 0)
            chunk_batch_args.append((current_batch_size, num_players, hole_cards, community_cards, all_cards, use_antithetic))
        
        # Run batches in parallel
        batch_results = parallel_execute(run_simulation_batch, chunk_batch_args)
        
        # Combine results
        for wins, ties in batch_results:
            for i in range(num_players):
                total_wins[i] += wins[i]
                total_ties[i] += ties[i]
        
        # Update simulations completed
        simulations_completed += chunk_size * (2 if use_antithetic else 1)
        
        # Calculate current win rates
        current_win_rates = []
        for i in range(num_players):
            # Calculate win percentage
            total_simulations = simulations_completed
            win_percentage = (total_wins[i] + total_ties[i]) / total_simulations * 100
            current_win_rates.append(win_percentage)
        
        # Check for convergence
        win_rate_history.append(current_win_rates)
        if simulations_completed >= iterations // 3:  # Only check after 1/3 of simulations
            convergence_reached = check_convergence(current_win_rates, win_rate_history)
        
        # Print progress
        elapsed = time.time() - start_time
        progress = simulations_completed / iterations * 100
        #print(f"Progress: {progress:.1f}% ({simulations_completed}/{iterations}), Time: {elapsed:.2f}s")
    
    # Calculate final win percentages
    results = {}
    total_simulations = simulations_completed
    
    for i in range(num_players):
        win_percentage = (total_wins[i] + total_ties[i]) / total_simulations * 100
        results[f"Player {i+1}"] = round(win_percentage, 2)
    
    # Print early termination info if applicable
    if convergence_reached:
        #print(f"Early termination at {simulations_completed} simulations due to convergence.")
        pass
    
    return results
