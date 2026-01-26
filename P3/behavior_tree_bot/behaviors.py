import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def do_nothing(state):
    return False

#
# ATTACK ACTIONS
#

# Send half the ships from strongest planet to last enemy planet
def finish_off_enemy(state):
    if len(state.enemy_planets()) != 1:
        return False

    strongest = find_strongest_safe_source_planet(state)
    target = state.enemy_planets()[0]

    if not strongest or not target:
        return False
    
    return issue_order(state, strongest.ID, target.ID, strongest.num_ships // 1)

# Send half the ships from strongest planet to weakest enemy planet
def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)

# Send needed ships form strongest planet to the weakest enemy planet, given the required ships for success are available
def attack_vulnerable_enemy(state):
    if len(state.my_fleets()) >= 1:
        return False
    
    # strongest non-threatened planet
    strongest_planet = find_strongest_safe_source_planet(state)
    if not strongest_planet:
        return False

    # find winnable enemy planets
    viable_targets = []
    for enemy in state.enemy_planets():
        distance = state.distance(strongest_planet.ID, enemy.ID)
        needed = enemy.num_ships + enemy.growth_rate * distance + 1
        if strongest_planet.num_ships > needed:
            viable_targets.append((enemy, needed))

    if not viable_targets:
        return False

    # weakest enemy and ships needed
    target, ships_needed = min(viable_targets, key=lambda t: t[0].num_ships)
    return issue_order(state, strongest_planet.ID, target.ID, ships_needed)

# Send needed ships form strongest planet to the highest growth enemy planet, given the required ships for success are available
def attack_highest_growth_enemy(state):
    if len(state.my_fleets()) >= 1:
        return False
    
    # strongest non-threatened planet
    strongest_planet = find_strongest_safe_source_planet(state)
    if not strongest_planet:
        return False

    viable_targets = []
    for enemy in state.enemy_planets():
        dist = state.distance(strongest_planet.ID, enemy.ID)
        needed = enemy.num_ships + enemy.growth_rate * dist + 1
        if strongest_planet.num_ships > needed:
            viable_targets.append(enemy)

    if not viable_targets:
        return False

    target = max(viable_targets, key=lambda p: p.growth_rate)
    ships = target.num_ships + target.growth_rate * state.distance(strongest_planet.ID, target.ID) + 1
    return issue_order(state, strongest_planet.ID, target.ID, ships)



#
# EXPANSION ACTIONS
#

# Send half the ships from strongest planet to weakest neutral planet, given the required ships for success are available
def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False

    return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)

# Send needed ships from strongest planet to the closest neutral planet, given the required ships for success are available
def spread_to_closest_neutral(state):
    if len(state.my_fleets()) >= 1:
        return False

    # strongest planet
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    if not strongest_planet:
        return False

    # find winnable neutral planets
    viable_targets = []
    for neutral in state.neutral_planets():
        distance = state.distance(strongest_planet.ID, neutral.ID)
        needed = neutral.num_ships + 1
        if strongest_planet.num_ships > needed:
            viable_targets.append((neutral, distance))

    if not viable_targets:
        return False

    target, _ = min(viable_targets, key=lambda t: t[1])
    ships = target.num_ships + 1
    return issue_order(state, strongest_planet.ID, target.ID, ships)



#
# DEFENCE ACTIONS
#

# Send needed ships from strongest planet to the weakest threatened planet, given the required ships for success are available
def defend_threatened_planet(state):
    # find planets with incoming attack that will lose
    threatened = []
    for planet in state.my_planets():
        incoming = sum(f.num_ships for f in state.enemy_fleets()
                       if f.destination_planet == planet.ID)
        if incoming > planet.num_ships:
            threatened.append((planet, incoming))

    if not threatened:
        return False

    # weakest targeted planet
    target, incoming = min(threatened, key=lambda t: t[0].num_ships)

    # strongest non-threatened planet
    strongest_planet = find_strongest_safe_source_planet(state)
    if not strongest_planet:
        return False

    ships_needed = incoming - target.num_ships + 1

    if strongest_planet.num_ships <= ships_needed:
        return False

    return issue_order(state, strongest_planet.ID, target.ID, ships_needed)

# Send ships to the weakest planet from the strongest so they are equal
def reinforce_weakest_planet(state):
    # strongest non-threatened planet
    strongest_planet = find_strongest_safe_source_planet(state)
    if not strongest_planet:
        return False
    
    # my weakest neutral planet
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if weakest_planet.ID == strongest_planet.ID:
        return False

    total_ships = strongest_planet.num_ships + weakest_planet.num_ships
    split_ships = total_ships // 2
    ships_needed = split_ships - weakest_planet.num_ships

    return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_needed)



# helper
def find_strongest_safe_source_planet(state):
    # All planets that are being targeted by the enemy
    targeted_ids = {f.destination_planet for f in state.enemy_fleets()}

    # My planets that are NOT targeted
    safe_planets = [p for p in state.my_planets() if p.ID not in targeted_ids]

    # strongest non-targeted planet
    strongest_planet = max(safe_planets, key=lambda p: p.num_ships, default=None)

    return strongest_planet