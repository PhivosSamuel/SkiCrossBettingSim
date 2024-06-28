import random
import numpy as np
from itertools import groupby
from skier import Skier
from odds import calculate_all_odds

def run_race(all_skiers, bets, odds):
    fallen_skiers = set()
    bump_skiers = {i: [] for i in range(1, 8)}
    race_results = {}
    payouts = {}
    stall_times = np.random.normal(2, 2, 7)
    stall_times = np.maximum(stall_times, 0)
    bump_stall_times = {i: np.random.choice(stall_times) for i in range(1, 8)}

    events = []
    finish_order = []
    finish_times = {}

    for bump in range(1, 8):
        for skier in all_skiers:
            if skier.number in fallen_skiers:
                events.append({
                    'skier_number': skier.number,
                    'bump_number': bump,
                    'status': 'Out',
                    'time': 0,
                    'stall_time': 0,
                    'total_time': skier.time
                })
                continue
            
            previous_time = skier.time
            event = skier.update(bump_skiers, bump_stall_times, fallen_skiers)
            time_for_bump = skier.time - previous_time

            event['total_time'] = skier.time
            events.append(event)

            if skier.has_fallen:
                fallen_skiers.add(skier.number)
                if skier.number not in finish_order:
                    finish_order.append(skier.number)
                    finish_times[skier.number] = float('inf')  # DNF skiers get infinite time
            elif bump == 7 and skier.number not in finish_order:
                finish_order.append(skier.number)
                finish_times[skier.number] = skier.time

    # Sort finish_order based on finish_times
    finish_order.sort(key=lambda x: finish_times[x])

    for skier in all_skiers:
        if skier.number in fallen_skiers:
            race_results[skier.number] = "DNF"
        else:
            race_results[skier.number] = skier.time

    for skier in all_skiers:
        if skier.number in fallen_skiers:
            payouts[skier.number] = 0
        else:
            position = finish_order.index(skier.number) + 1
            if position <= 3:
                odds_for_position = odds[skier.number][position]
                payout = bets[skier.number] * odds_for_position
                payouts[skier.number] = payout
            else:
                payouts[skier.number] = 0

    return events, finish_order, race_results, bump_skiers, payouts, finish_order[:3], [race_results[skier] for skier in finish_order[:3] if race_results[skier] != "DNF"], fallen_skiers

def print_bump_status(bump_skiers, fallen_skiers):
    for bump in range(1, 7):
        print(f"\nBump {bump}:")
        for skier_number, status in bump_skiers[bump]:
            print(f"Skier {skier_number} - {status}")

def betting(all_skiers, user_money):
    bets = {}
    odds = calculate_all_odds(all_skiers)

    print("Skiers with their stats and odds:")
    print(f"Number of skiers: {len(all_skiers)}")
    for skier in all_skiers:
        print(f"Skier {skier.number} - Experience: {skier.experience}, Talent: {skier.talent}, Speed: {skier.speed}")
        for position in range(1, 4):  # Positions 1, 2, 3
            odds_value = round(odds[skier.number][position], 2)
            print(f"Odds for placing {position}st: {odds_value}")

    for skier in all_skiers:
        while True:
            try:
                print(f"How much do you want to bet on Skier {skier.number}? (Available funds: ${user_money:.2f})")
                bet = float(input())
                if bet < 0 or bet > user_money:
                    print("Invalid bet. Please enter a number between 0 and your remaining money.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        user_money -= bet
        bets[skier.number] = bet

    return bets, user_money  # Return the remaining funds
