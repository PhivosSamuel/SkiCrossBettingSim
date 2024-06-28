def calculate_odds(skier, all_skiers, position):
    def weighted_score(s):
        return 0.45 * s.speed + 0.30 * s.talent + 0.25 * s.experience

    scores = [weighted_score(s) for s in all_skiers]
    total_score = sum(scores)
    skier_score = weighted_score(skier)

    # Calculate relative strength
    relative_strength = skier_score / (total_score / len(all_skiers))

    # Base odds calculation
    base_odds = 1 / relative_strength 

    # Position adjustment considering typical 3 finishers
    if position <= 3:
        position_adjustment = {1: 1.0, 2: 0.8, 3: 0.6}[position]
    else:
        position_adjustment = 0.1  # Very low odds for positions beyond 3rd

    adjusted_odds = base_odds * position_adjustment

    # Apply scaling factor and house edge
    x = 3.5  # Scaling factor to bring odds down  
    house_edge = 0.85  # 15% house edge
    final_odds = adjusted_odds * x * house_edge

    return max(1.1, final_odds)

def calculate_all_odds(all_skiers):
    odds = {}
    for skier in all_skiers:
        odds[skier.number] = {
            position: calculate_odds(skier, all_skiers, position)
            for position in range(1, len(all_skiers) + 1)
        }
    return odds