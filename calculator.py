from evaluator import compare_hands
from simulator import monte_carlo_simulation
from utils.card import validate_cards, enumerate_remaining_cards
from utils.parallel import get_computation_device
import json
import os
import time

def calculate_win_rate(num_players, hole_cards, community_cards=None):
    """
    Calculate win rate percentages for Texas Hold'em players.
    
    Args:
        num_players (int): Number of players (2-9)
        hole_cards (list): List of hole card pairs for each player
        community_cards (list, optional): List of community cards (0-5)
    
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
    
    # Validate all cards
    all_cards = [card for hand in hole_cards for card in hand] + community_cards
    validate_cards(all_cards)
    
    # Pre-flop calculations (0 community cards) or few community cards: use Monte Carlo
    if len(community_cards) < 3:
        return monte_carlo_simulation(num_players, hole_cards, community_cards)
    
    # Post-flop calculations: use exact enumeration
    return exact_enumeration(num_players, hole_cards, community_cards)

def exact_enumeration(num_players, hole_cards, community_cards):
    """
    Calculate exact win probabilities by enumerating all possible remaining card combinations.
    
    Args:
        num_players (int): Number of players
        hole_cards (list): List of hole card pairs for each player
        community_cards (list): List of community cards (3-5)
    
    Returns:
        dict: Win percentages for each player
    """
    # Initialize counters
    wins = [0] * num_players
    total_hands = 0
    
    # Flatten all known cards
    all_cards = [card for hand in hole_cards for card in hand] + community_cards
    
    # Calculate how many more cards need to be drawn
    remaining_to_draw = 5 - len(community_cards)
    
    # If we already have 5 community cards, just evaluate once
    if remaining_to_draw == 0:
        winners = compare_hands(hole_cards, community_cards)
        for winner in winners:
            wins[winner] += 1
        total_hands = 1
    else:
        # Enumerate all possible remaining card combinations
        possible_draws = enumerate_remaining_cards(all_cards, remaining_to_draw)
        total_hands = len(possible_draws)
        
        # Evaluate each possible board
        for draw in possible_draws:
            complete_board = community_cards + list(draw)
            winners = compare_hands(hole_cards, complete_board)
            
            # Split the win among tied players
            win_value = 1.0 / len(winners)
            for winner in winners:
                wins[winner] += win_value
    
    # Calculate win percentages
    results = {}
    for i in range(num_players):
        win_percentage = (wins[i] / total_hands) * 100
        results[f"Player {i+1}"] = round(win_percentage, 2)
    
    return results

def load_test_data(file_path="data/test_data.json"):
    """
    Load test data from a JSON file.
    
    Args:
        file_path (str): Path to the test data file
    
    Returns:
        list: List of test cases
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def run_tests(test_cases):
    """
    Run tests using the test cases and compare with collected results.
    
    Args:
        test_cases (list): List of test cases
    
    Returns:
        list: List of test results with calculated win rates and comparison
    """
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"Running test case {i+1}...")
        
        # Extract test data
        num_players = test_case["num_players"]
        hole_cards = test_case["hole_cards"]
        community_cards = test_case["community_cards"]
        expected_win_rates = test_case["collected_win_rates"]
        
        # Record start time
        start_time = time.time()
        
        # Calculate win rates
        calculated_win_rates = calculate_win_rate(num_players, hole_cards, community_cards)
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Compare results
        differences = {}
        for player, expected_rate in expected_win_rates.items():
            calculated_rate = calculated_win_rates[player]
            diff = abs(calculated_rate - expected_rate)
            differences[player] = diff
        
        # Determine if test passed
        passed = all(diff <= 1.0 for diff in differences.values())
        
        # Create result record
        result = {
            "test_case": i+1,
            "num_players": num_players,
            "hole_cards": hole_cards,
            "community_cards": community_cards,
            "expected_win_rates": expected_win_rates,
            "calculated_win_rates": calculated_win_rates,
            "differences": differences,
            "execution_time": elapsed_time,
            "passed": passed
        }
        
        results.append(result)
        
        # Print result summary
        print(f"Test case {i+1} - {'PASSED' if passed else 'FAILED'}")
        print(f"Execution time: {elapsed_time:.2f} seconds")
        print("Expected vs Calculated:")
        for player in expected_win_rates:
            print(f"  {player}: {expected_win_rates[player]:.2f}% vs {calculated_win_rates[player]:.2f}%")
        print()
    
    return results

def save_test_results(results, file_path="data/test_result.json"):
    """
    Save test results to a JSON file.
    
    Args:
        results (list): List of test results
        file_path (str): Path to save the results
    """
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Test results saved to {file_path}")

def run_all_tests():
    """Run all tests and save results."""
    # Print computation device info
    computation_device = get_computation_device()
    print(f"Using computation device: {computation_device}")
    print("Note: GPU acceleration will significantly speed up Monte Carlo simulations if available.\n")
    
    # Load test data
    test_cases = load_test_data()
    
    # Run tests
    results = run_tests(test_cases)
    
    # Save results
    save_test_results(results)
    
    # Print summary
    passed_count = sum(1 for result in results if result["passed"])
    total_count = len(results)
    
    print(f"\nSummary: {passed_count}/{total_count} tests passed")
    
    return passed_count == total_count


if __name__ == "__main__":
    # Check if we should run tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_all_tests()
    else:
        # Example usage
        num_players = 3
        hole_cards = [["AH", "KD"], ["KS", "QC"], ["QS", "JC"]]
        community_cards=["2C", "7D", "8S"]
        
        win_rates = calculate_win_rate(num_players, hole_cards, community_cards)
        print("Win Rates:")
        for player, rate in win_rates.items():
            print(f"{player}: {rate}%")

