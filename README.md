# Texas Hold'em Win Rate Calculator

A comprehensive win rate calculator for Texas Hold'em poker. This project provides fast and accurate calculation of winning probabilities for poker hands across different stages of the game.

## Features

- **Multiple Player Support**: Calculate win rates for 2-9 players simultaneously
- **Full Game Stage Support**: 
  - Pre-flop (no community cards)
  - Flop (3 community cards)
  - Turn (4 community cards)
  - River (5 community cards)
- **Adaptive Algorithms**:
  - Monte Carlo simulation for pre-flop analysis with optimized iteration counts
  - Exact enumeration for post-flop calculations, providing 100% accuracy
- **Performance Optimizations**:
  - Parallel computation leveraging multiple CPU cores
  - Optional GPU acceleration via Numba (if available)
  - Automated selection of optimal algorithm based on game stage
- **Comprehensive Testing Framework**: Built-in test suite with benchmark cases

## Project Structure

```
Texas_Holdem_WR_Calculator/
├── calculator.py        # Main entry point and win rate calculation logic
├── evaluator.py         # Hand evaluation using pypokerengine
├── simulator.py         # Monte Carlo simulation engine
├── utils/
│   ├── card.py          # Card handling utilities
│   └── parallel.py      # Parallelization helpers
├── data/
│   ├── test_data.json   # Test cases with expected results
│   └── test_result.json # Test execution results
├── tests/
│   ├── test_calculator.py  # Calculator module tests
│   └── test_evaluator.py   # Evaluator module tests
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker services configuration
└── requirements.txt     # Python dependencies
```

## Algorithm Details

- **Pre-flop Calculations**: Uses Monte Carlo simulation with adaptive iteration count:
  - 2-3 players: 120,000 iterations
  - 4-6 players: 100,000 iterations
  - 7-9 players: 80,000 iterations

- **Post-flop Calculations**: Uses exact enumeration of all possible remaining card combinations for 100% accuracy.

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Texas_Holdem_WR_Calculator.git
cd Texas_Holdem_WR_Calculator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the calculator:
```bash
python calculator.py
```

### Docker Installation

You can also run the application using Docker:

1. Build and run with Docker Compose:
```bash
docker-compose up
```

2. For interactive mode:
```bash
docker-compose run poker-interactive
```

3. Run custom calculations:
```bash
docker-compose run poker-calculator python calculator.py
```

See [DOCKER_USAGE.md](DOCKER_USAGE.md) for comprehensive Docker instructions.

## Usage Examples

### Basic Usage

```python
from calculator import calculate_win_rate

# Example usage
num_players = 3
hole_cards = [["AH", "KD"], ["KS", "QC"], ["QS", "JC"]]
community_cards = ["2C", "7D", "8S"]

win_rates = calculate_win_rate(num_players, hole_cards, community_cards)
print("Win Rates:")
for player, rate in win_rates.items():
    print(f"{player}: {rate}%")
```

### Card Notation

Cards are represented as 2-character strings:
- First character: Card rank (2-9, T, J, Q, K, A)
- Second character: Card suit (S=Spades, H=Hearts, D=Diamonds, C=Clubs)

Examples: "AH" = Ace of Hearts, "TD" = Ten of Diamonds, "2C" = Two of Clubs

### Running Tests

Run the built-in test suite:
```bash
python calculator.py --test
```

## Performance

Performance characteristics:
- Pre-flop calculations: ~3 seconds (with parallel processing)
- Post-flop calculations: <1 second (faster with fewer cards to enumerate)
- Parallel processing can significantly improve speed on multi-core systems

## Requirements

- Python 3.8+
- PyPokerEngine
- NumPy
- Numba (optional, for GPU acceleration)

## License

[MIT License](LICENSE)
