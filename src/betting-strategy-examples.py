import random
from race import run_race
from odds import calculate_all_odds
from skier import Skier
import numpy as np

NUM_SIMULATIONS = 1000
INITIAL_BALANCE = 100
NUM_ROUNDS = 3
NUM_SKIERS = 8

def create_skiers():
    return [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, NUM_SKIERS + 1)]

def simulate_round(balance, strategy):
    all_skiers = create_skiers()
    odds = calculate_all_odds(all_skiers)
    bets = strategy(balance, odds)
    
    events, finish_order, race_results, bump_skiers, payouts, winning_skiers, winning_times, fallen_skiers = run_race(all_skiers, bets, odds)
    
    round_winnings = sum(payouts.values())
    new_balance = balance - sum(bets.values()) + round_winnings
    return max(0, new_balance)

def simulate_game(strategy):
    balance = INITIAL_BALANCE
    for _ in range(NUM_ROUNDS):
        if balance == 0:
            break
        balance = simulate_round(balance, strategy)
    return balance

def run_simulations(strategy):
    return [simulate_game(strategy) for _ in range(NUM_SIMULATIONS)]

def calculate_percentile(balance, all_balances):
    return np.percentile(all_balances, np.searchsorted(np.sort(all_balances), balance) / len(all_balances) * 100)

# Betting strategies
def spread_equally(balance, odds):
    bet_amount = balance / NUM_SKIERS
    return {i: bet_amount for i in range(1, NUM_SKIERS + 1)}

def top_three(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1])  # Sort by odds of finishing first
    top_three_skiers = [skier for skier, _ in sorted_skiers[:3]]
    bet_amount = balance / 3
    return {skier: bet_amount if skier in top_three_skiers else 0 for skier in range(1, NUM_SKIERS + 1)}

def bottom_three(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1], reverse=True)  # Sort by odds of finishing first (reversed)
    bottom_three_skiers = [skier for skier, _ in sorted_skiers[:3]]
    bet_amount = balance / 3
    return {skier: bet_amount if skier in bottom_three_skiers else 0 for skier in range(1, NUM_SKIERS + 1)}

def mix_top_bottom(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1])
    top_two = [skier for skier, _ in sorted_skiers[:2]]
    bottom_two = [skier for skier, _ in sorted_skiers[-2:]]
    bet_amount = balance / 4
    return {skier: bet_amount if skier in top_two + bottom_two else 0 for skier in range(1, NUM_SKIERS + 1)}

def kelly_criterion(balance, odds):
    bets = {}
    for skier, skier_odds in odds.items():
        p = 1 / skier_odds[1]  # Probability of winning (inverse of odds)
        q = 1 - p  # Probability of losing
        f = (p * skier_odds[1] - q) / skier_odds[1]  # Kelly fraction
        bet_amount = max(0, f * balance)  # Ensure non-negative bet
        bets[skier] = bet_amount
    return bets

def kelly_criterion_favorite(balance, odds):
    # Find the favorite (skier with the lowest odds, which means highest chance of winning)
    favorite_skier = min(odds, key=lambda x: odds[x][1])
    favorite_odds = odds[favorite_skier][1]

    # Calculate Kelly Criterion for the favorite
    p = 1 / favorite_odds  # Probability of winning
    q = 1 - p  # Probability of losing
    f = (p * favorite_odds - q) / favorite_odds  # Kelly fraction

    # Calculate bet amount, ensuring it's non-negative
    bet_amount = max(0, f * balance)

    # Create a dictionary with 0 bets for all skiers except the favorite
    bets = {skier: 0 for skier in odds}
    bets[favorite_skier] = bet_amount

    return bets

def all_in_on_favorite(balance, odds):
    favorite = min(odds.items(), key=lambda x: x[1][1])[0]
    return {skier: balance if skier == favorite else 0 for skier in range(1, NUM_SKIERS + 1)}

def all_in_on_underdog(balance, odds):
    underdog = max(odds.items(), key=lambda x: x[1][1])[0]
    return {skier: balance if skier == underdog else 0 for skier in range(1, NUM_SKIERS + 1)}

def bet_on_middle(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1])
    middle_skiers = [skier for skier, _ in sorted_skiers[3:5]]
    bet_amount = balance / 2
    return {skier: bet_amount if skier in middle_skiers else 0 for skier in range(1, NUM_SKIERS + 1)}

def proportional_to_odds(balance, odds):
    total_odds = sum(1/odds[skier][1] for skier in range(1, NUM_SKIERS + 1))
    return {skier: balance * (1/odds[skier][1]) / total_odds for skier in range(1, NUM_SKIERS + 1)}

def inverse_proportional_to_odds(balance, odds):
    total_inverse_odds = sum(odds[skier][1] for skier in range(1, NUM_SKIERS + 1))
    return {skier: balance * odds[skier][1] / total_inverse_odds for skier in range(1, NUM_SKIERS + 1)}

def martingale(balance, odds):
    global martingale_bet, martingale_skier
    if martingale_bet is None or martingale_skier is None:
        martingale_bet = balance * 0.1
        martingale_skier = random.randint(1, NUM_SKIERS)
    
    bet = min(martingale_bet, balance)
    result = {skier: bet if skier == martingale_skier else 0 for skier in range(1, NUM_SKIERS + 1)}
    
    martingale_bet *= 2
    martingale_skier = random.randint(1, NUM_SKIERS)
    
    return result

def fibonacci(balance, odds):
    global fib_sequence, fib_index
    if fib_sequence is None or fib_index is None:
        fib_sequence = [1, 1]
        fib_index = 0
    
    while fib_sequence[-1] < balance:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    
    bet = min(fib_sequence[fib_index] * (balance * 0.01), balance)
    chosen_skier = random.randint(1, NUM_SKIERS)
    result = {skier: bet if skier == chosen_skier else 0 for skier in range(1, NUM_SKIERS + 1)}
    
    fib_index = (fib_index + 1) % len(fib_sequence)
    
    return result

def d_alembert(balance, odds):
    global dalembert_unit, dalembert_skier
    if dalembert_unit is None or dalembert_skier is None:
        dalembert_unit = balance * 0.01
        dalembert_skier = random.randint(1, NUM_SKIERS)
    
    bet = min(dalembert_unit, balance)
    result = {skier: bet if skier == dalembert_skier else 0 for skier in range(1, NUM_SKIERS + 1)}
    
    dalembert_unit += balance * 0.01
    dalembert_skier = random.randint(1, NUM_SKIERS)
    
    return result

def oscar_grind(balance, odds):
    global oscar_bet, oscar_skier, oscar_target
    if oscar_bet is None or oscar_skier is None or oscar_target is None:
        oscar_bet = balance * 0.01
        oscar_skier = random.randint(1, NUM_SKIERS)
        oscar_target = balance * 0.1
    
    bet = min(oscar_bet, balance, oscar_target)
    result = {skier: bet if skier == oscar_skier else 0 for skier in range(1, NUM_SKIERS + 1)}
    
    if bet == oscar_target:
        oscar_bet = balance * 0.01
        oscar_target = balance * 0.1
    else:
        oscar_bet += balance * 0.01
    
    oscar_skier = random.randint(1, NUM_SKIERS)
    
    return result

def paroli(balance, odds):
    global paroli_bet, paroli_skier, paroli_wins
    if paroli_bet is None or paroli_skier is None or paroli_wins is None:
        paroli_bet = balance * 0.01
        paroli_skier = random.randint(1, NUM_SKIERS)
        paroli_wins = 0
    
    bet = min(paroli_bet, balance)
    result = {skier: bet if skier == paroli_skier else 0 for skier in range(1, NUM_SKIERS + 1)}
    
    if paroli_wins == 3:
        paroli_bet = balance * 0.01
        paroli_wins = 0
    else:
        paroli_bet *= 2
        paroli_wins += 1
    
    paroli_skier = random.randint(1, NUM_SKIERS)
    
    return result

def bet_on_top_speed(balance, odds):
    skiers = create_skiers()  # Assuming this function is available
    fastest_skier = max(skiers, key=lambda s: s.speed).number
    return {skier: balance if skier == fastest_skier else 0 for skier in range(1, NUM_SKIERS + 1)}

def bet_on_top_talent(balance, odds):
    skiers = create_skiers()
    most_talented_skier = max(skiers, key=lambda s: s.talent).number
    return {skier: balance if skier == most_talented_skier else 0 for skier in range(1, NUM_SKIERS + 1)}

def bet_on_top_experience(balance, odds):
    skiers = create_skiers()
    most_experienced_skier = max(skiers, key=lambda s: s.experience).number
    return {skier: balance if skier == most_experienced_skier else 0 for skier in range(1, NUM_SKIERS + 1)}

def conservative_spread(balance, odds):
    bet_amount = balance * 0.5 / NUM_SKIERS
    return {skier: bet_amount for skier in range(1, NUM_SKIERS + 1)}

def conservative_top_three(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1])
    top_three_skiers = [skier for skier, _ in sorted_skiers[:3]]
    bet_amount = balance * 0.5 / 3
    return {skier: bet_amount if skier in top_three_skiers else 0 for skier in range(1, NUM_SKIERS + 1)}

def bet_on_balanced_skier(balance, odds):
    skiers = create_skiers()
    balanced_skier = min(skiers, key=lambda s: (s.speed - s.talent)**2 + (s.talent - s.experience)**2 + (s.experience - s.speed)**2).number
    return {skier: balance if skier == balanced_skier else 0 for skier in range(1, NUM_SKIERS + 1)}

def progressive_betting(balance, odds):
    sorted_skiers = sorted(odds.items(), key=lambda x: x[1][1])
    total_parts = sum(range(1, NUM_SKIERS + 1))
    bets = {}
    for i, (skier, _) in enumerate(sorted_skiers, 1):
        bets[skier] = balance * (NUM_SKIERS - i + 1) / total_parts
    return bets


strategies = {
    "Spread Equally": spread_equally,
    "Top Three": top_three,
    "Bottom Three": bottom_three,
    "Mix Top and Bottom": mix_top_bottom,
    "Kelly Criterion": kelly_criterion,
    "All-in on Favorite": all_in_on_favorite,
    "All-in on Underdog": all_in_on_underdog,
    "Bet on Middle": bet_on_middle,
    "Proportional to Odds": proportional_to_odds,
    "Inverse Proportional to Odds": inverse_proportional_to_odds,
    "Martingale": martingale,
    "Fibonacci": fibonacci,
    "D'Alembert": d_alembert,
    "Oscar's Grind": oscar_grind,
    "Paroli": paroli,
    "Bet on Top Speed": bet_on_top_speed,
    "Bet on Top Talent": bet_on_top_talent,
    "Bet on Top Experience": bet_on_top_experience,
    "Conservative Spread": conservative_spread,
    "Conservative Top Three": conservative_top_three,
    "Bet on Balanced Skier": bet_on_balanced_skier,
    "Progressive Betting": progressive_betting,
    "Kelly Criterion (Favorite Only)": kelly_criterion_favorite,
}

def main():
    results = {}
    all_final_balances = []
    global_vars = [
        'martingale_bet', 'martingale_skier', 'fib_sequence', 'fib_index',
        'dalembert_unit', 'dalembert_skier', 'oscar_bet', 'oscar_skier',
        'oscar_target', 'paroli_bet', 'paroli_skier', 'paroli_wins'
    ]

    for name, strategy in strategies.items():
        # Reset global variables for stateful strategies
        for var in global_vars:
            globals()[var] = None

        final_balances = run_simulations(strategy)
        avg_balance = sum(final_balances) / len(final_balances)
        results[name] = avg_balance
        all_final_balances.extend(final_balances)
        print(f"{name}: ${avg_balance:.2f}")
    
    overall_average = sum(results.values()) / len(results)
    print(f"\nOverall Average: ${overall_average:.2f}")

    # Calculate percentile for a given balance
    target_balance = 100  # You can change this value
    percentile = calculate_percentile(target_balance, all_final_balances)
    print(f"\nIf your end balance is ${target_balance}, you are better than {percentile:.2f}% of players.")

if __name__ == "__main__":
    main()