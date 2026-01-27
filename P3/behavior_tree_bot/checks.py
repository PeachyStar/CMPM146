def if_under_attack(state):
    # Returns True if any enemy fleet is heading toward one of our planets 
    my_planet_ids = {p.ID for p in state.my_planets()}
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in my_planet_ids:
            return True
    return False

def if_neutral_available(state):
    # Check if there are any planets not owned by anyone 
    return any(state.neutral_planets())
