from flask import Flask, render_template, request, jsonify, logging
import random
import logging
import traceback
from race import run_race, betting, print_bump_status
from odds import calculate_all_odds
from skier import Skier

app = Flask(__name__, template_folder='../templates',static_folder='../static')

@app.route('/')
def index():
    return render_template('index.html', balance=100)

all_skiers = []
odds = []

@app.route('/start_game', methods=['POST'])
def start_game():
    global all_skiers, odds
    all_skiers = [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, 9)]
    odds = calculate_all_odds(all_skiers)
    # Print skier stats
    #print("Skiers with their stats and odds:")
    #print(f"Number of skiers: {len(all_skiers)}")
    for skier in all_skiers:
        print(f"Skier {skier.number} - Experience: {skier.experience}, Talent: {skier.talent}, Speed: {skier.speed}")
    return jsonify(odds)

@app.route('/start_round', methods=['POST'])
def start_round():
    global all_skiers, odds
    all_skiers = [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, 9)]
    odds = calculate_all_odds(all_skiers)
    # Print skier stats
    print("Skiers with their stats and odds:")
    print(f"Number of skiers: {len(all_skiers)}")
    for skier in all_skiers:
        print(f"Skier {skier.number} - Experience: {skier.experience}, Talent: {skier.talent}, Speed: {skier.speed}")
    return jsonify(odds)

@app.route('/get_skier_stats', methods=['GET'])
def get_skier_stats():
    global all_skiers
    round_number = request.args.get('round_number', type=int)
    skier_stats = {skier.number: {'experience': skier.experience, 'talent': skier.talent, 'speed': skier.speed} for skier in all_skiers}
    return jsonify(skier_stats)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    global all_skiers, odds
    try:
        data = request.get_json()
        user_money = float(data['balance'])
        bets = {int(bet['skier_id']): float(bet['bet_amount']) for bet in data['bets']}

        # Check if total bet amount is greater than balance
        total_bet_amount = sum(bets.values())
        if total_bet_amount > user_money:
            return jsonify(error="Total bet amount cannot be greater than balance"), 400

        user_money -= total_bet_amount

        # Simulate the race and calculate payouts
        events, finish_order, race_results, bump_skiers, payouts, winning_skiers, winning_times, fallen_skiers = run_race(all_skiers, bets, odds)

        # Calculate round winnings
        round_winnings = sum(payouts.values())

        # Update user money with the winnings from this round
        user_money = user_money + round_winnings  # Add the winnings to the balance

        return jsonify(
            new_balance=user_money,
            round_winnings=round_winnings,
            payouts=payouts,
            finish_order=finish_order,
            race_results=race_results,
            events=events,
            skier_stats={skier.number: {'experience': skier.experience, 'talent': skier.talent, 'speed': skier.speed} for skier in all_skiers}
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify(error=str(e)), 500

@app.route('/get_new_odds', methods=['GET'])
def get_new_odds():
    global all_skiers, odds
    all_skiers = [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, 9)]
    odds = calculate_all_odds(all_skiers)
    return jsonify(odds)

def main():
    # Create a list of Skier objects with random attributes
    all_skiers = [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, 9)]
    
    # Initial amount of money the user has
    user_money = 100
    total_winnings = 0  # To track winnings across all rounds
    
    # Run the simulation for three rounds
    for round_number in range(1, 4):
        all_skiers = [Skier(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(1, 9)]
        print(f"\n--- Round {round_number} ---")
        odds = calculate_all_odds(all_skiers)
        bets, user_money = betting(all_skiers, user_money)


        events, finish_order, race_results, bump_skiers, payouts, winning_skiers, winning_times, fallen_skiers = run_race(all_skiers, bets, odds)
        print_bump_status(bump_skiers, fallen_skiers)

        # Print race results and winnings
        print("Race Rankings:")
        for i, skier_number in enumerate(finish_order, start=1):
            result = race_results[skier_number]
            suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
            print(f"{i}{suffix} place: Skier {skier_number} - Time: {result if result == 'DNF' else f'{result:.2f} seconds'}")

        print("\nSkier Payouts:")
        round_winnings = 0
        for skier_number, winnings in payouts.items():
            print(f"Skier {skier_number}: ${winnings:.2f}")
            round_winnings += winnings

        # Update user money with the winnings from this round
        user_money = user_money + round_winnings  # Add the winnings to the balance

    print(f"\nFinal Balance after 3 Rounds: ${user_money:.2f}")

if __name__ == "__main__":
    app.run(debug=True)
