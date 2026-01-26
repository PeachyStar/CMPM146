def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def have_largest_fleet(state):
    my_total = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    return my_total > enemy_total

def if_planet_threatened(state):
    my_planet_ids = {p.ID for p in state.my_planets()}
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in my_planet_ids:
            return True
    return False
