import sys
from planet_wars import issue_order

def defend_smart(state):
    # Find threatened planets and reinforce them from safe ones [cite: 58, 79]
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()
    for planet in my_planets:
        incoming_enemy = sum(f.num_ships for f in enemy_fleets if f.destination_planet == planet.ID)
        if incoming_enemy > planet.num_ships:
            needed = incoming_enemy - planet.num_ships + 1
            others = [p for p in my_planets if p.ID != planet.ID]
            if not others: continue
            best_donor = max(others, key=lambda p: p.num_ships)
            if best_donor.num_ships > needed:
                return issue_order(state, best_donor.ID, planet.ID, int(needed))
    return False

def attack_high_growth(state):
    # Targets planets based on growth rate vs cost to capture [cite: 58, 72, 79]
    my_planets = state.my_planets()
    if not my_planets: return False
    source = max(my_planets, key=lambda p: p.num_ships)
    targets = state.not_my_planets()
    if not targets: return False

    def score(target):
        dist = state.distance(source.ID, target.ID)
        needed = target.num_ships + (target.growth_rate * dist if target.owner != 0 else 0) + 1
        if source.num_ships <= needed: return -1
        return (target.growth_rate ** 2) / (dist * (needed + 1))

    best_target = max(targets, key=score, default=None)
    if best_target and score(best_target) > 0:
        dist = state.distance(source.ID, best_target.ID)
        needed = best_target.num_ships + (best_target.growth_rate * dist if best_target.owner != 0 else 0) + 1
        return issue_order(state, source.ID, best_target.ID, int(needed))
    return False
