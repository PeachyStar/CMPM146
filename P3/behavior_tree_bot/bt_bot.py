import logging, sys, os

# This adds the current directory to the path so it can find planet_wars.py
# and the behavior_tree_bot folder.
sys.path.insert(0, os.getcwd())

from planet_wars import PlanetWars, finish_turn
from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

def setup_behavior_tree():
    root = Selector(name='Main Strategy')

    # Priority 1: Defense 
    # Ensure 'defend_threatened_planet' exists in behaviors.py
    defense = Sequence(name='Defense')
    defense.child_nodes = [
        Check(if_planet_threatened), 
        Action(defend_threatened_planet)
    ]

    # Priority 2: Expansion
    spread = Sequence(name='Spread')
    spread.child_nodes = [
        Check(if_neutral_planet_available), 
        Action(spread_to_weakest_neutral_planet)
    ]

    # Priority 3: Attack
    attack = Sequence(name='Attack')
    attack.child_nodes = [
        Check(have_largest_fleet), 
        Action(attack_weakest_enemy_planet)
    ]

    # Assemble the tree
    root.child_nodes = [defense, spread, attack, Action(attack_weakest_enemy_planet)]
    return root

if __name__ == '__main__':
    # Use an absolute path for the log to ensure it writes where you can see it
    log_path = os.path.join(os.getcwd(), 'bt_bot.log')
    logging.basicConfig(filename=log_path, filemode='w', level=logging.DEBUG)
    
    logging.info("Starting Bot...")
    
    try:
        behavior_tree = setup_behavior_tree()
        logging.info("Tree Constructed Successfully:")
        logging.info('\n' + behavior_tree.tree_to_string())

        map_data = ''
        while True:
            current_line = sys.stdin.readline()
            if not current_line:
                break 
            if current_line.startswith("go"):
                state = PlanetWars(map_data)
                behavior_tree.execute(state)
                finish_turn() # Sends "go" to Java [cite: 83, 85]
                map_data = ''
            else:
                map_data += current_line
    except Exception as e:
        logging.exception("A fatal error occurred:")
