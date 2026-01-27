import sys
from planet_wars import issue_order

# If a planet has more incoming enemy ships than it has, send needed rienforcements from strongest planet.
def defend_smart(state):
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    for planet in my_planets:
        incoming_enemy = sum(f.num_ships for f in enemy_fleets if f.destination_planet == planet.ID)
        if incoming_enemy > planet.num_ships:
            # number of ships needed to save planet
            needed = incoming_enemy - planet.num_ships + 1
            
            # send ships from the strongest planet that is not the one being attacked
            others = [p for p in my_planets if p.ID != planet.ID]
            if not others: continue
            best_donor = max(others, key=lambda p: p.num_ships)
            if best_donor.num_ships > needed:
                return issue_order(state, best_donor.ID, planet.ID, int(needed))
    return False

# Send ships from my strongest planet to the best neutral or enemy planet with high growth
def attack_high_growth(state): 
    my_planets = state.my_planets()
    if not my_planets: return False

    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    
    targets = state.not_my_planets()
    if not targets: return False

    # assign targets a score that favors high growth but balances for distance and strength
    def score(target):
        dist = state.distance(strongest_planet.ID, target.ID)
        needed = target.num_ships + (target.growth_rate * dist if target.owner != 0 else 0) + 1
        if strongest_planet.num_ships <= needed: return -1
        return (target.growth_rate ** 2) / (dist * (needed + 1))

    best_target = max(targets, key=score, default=None)
    if best_target and score(best_target) > 0:
        dist = state.distance(strongest_planet.ID, best_target.ID)
        needed = best_target.num_ships + (best_target.growth_rate * dist if best_target.owner != 0 else 0) + 1
        return issue_order(state, strongest_planet.ID, best_target.ID, int(needed))
    
    return False
