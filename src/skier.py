import random

class Skier:
    def __init__(self, number, experience, talent, speed):
        self.number = number
        self.experience = experience
        self.talent = talent
        self.speed = speed
        self.time = 0  # Time to complete the race in seconds
        self.fell_bumps = set()
        self.stalled_bumps = set()
        self.current_bump = 1
        self.has_fallen = False 
        self.winnings = 0

    def calculate_fall_chance(self):
        fall_base_chance = 12  # 12% base chance of falling
        experience_bonus = self.experience  # Maximum 10% bonus based on experience
        fall_chance = fall_base_chance - experience_bonus
        return max(fall_chance, 0)  # Ensure fall chance is not negative

    def calculate_stall_chance(self):
        stall_base_chance = 25  # 25% base chance of stalling
        talent_bonus = self.talent  # Maximum 20% bonus based on talent
        stall_chance = stall_base_chance - (talent_bonus * 2)
        return max(stall_chance, 0)  # Ensure stall chance is not negative

    def update(self, bump_skiers, bump_stall_times, fallen_skiers):
        if self.current_bump > 7 or self.has_fallen:  # Stop updating after the finish line
            return {
                'skier_number': self.number,
                'bump_number': self.current_bump,
                'status': 'Finished' if self.current_bump > 7 else 'Fallen',
                'time': 0,
                'stall_time': 0,
                'total_time': self.time
            }

        # Common calculations for all bumps
        base_bump_time = 2.6
        speed_reduction = min(self.speed * 0.2, 3)
        bump_time = max(base_bump_time - speed_reduction, 1)
        bump_time += random.uniform(-0.5, 0.5)
        self.time += bump_time

        event = {
            'skier_number': self.number,
            'bump_number': self.current_bump,
            'time': bump_time,
            'stall_time': 0,
            'total_time': self.time
        }

        if self.current_bump == 7:  # Handle Bump 7 as the finish line without stalling or falling
            event['status'] = 'Finished'
            self.current_bump += 1
            return event

        # Logic for bumps 1 to 6
        if self.calculate_fall_chance() / 100 > random.random():
            self.fell_bumps.add(self.current_bump)
            fallen_skiers.add(self.number)
            self.has_fallen = True
            event['status'] = 'Fell'
            return event

        if self.calculate_stall_chance() / 100 > random.random():
            self.stalled_bumps.add(self.current_bump)
            stall_time = bump_stall_times.get(self.current_bump, 0)
            self.time += stall_time
            event['stall_time'] = stall_time
            event['total_time'] = self.time
            event['status'] = 'Stalled'
        else:
            event['status'] = 'Cleared'

        self.current_bump += 1
        return event
