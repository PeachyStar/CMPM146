import logging, sys, os

# Force path to find planet_wars.py in the folder above [cite: 12, 18]
sys.path.insert(0, os.getcwd())

from planet_wars import PlanetWars, finish_turn
from behavior_tree_bot.behaviors import defend_smart, attack_high_growth
from behavior_tree_bot.checks import if_under_attack, if_neutral_available
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

def setup_behavior_tree():
    root = Selector(name='Main Strategy')

    # 1. Defense (Priority 1)
    defense = Sequence(name='Defense')
    defense.child_nodes = [Check(if_under_attack), Action(defend_smart)]

    # 2. Attack / Expansion (Priority 2)
    # Using the high-growth logic to beat the Production/Spread bots
    attack = Action(attack_high_growth)

    root.child_nodes = [defense, attack]
    return root

if __name__ == '__main__':
    logging.basicConfig(filename='bt_bot.log', filemode='w', level=logging.DEBUG)
    logging.info("Initializing Bot...")
    try:
        behavior_tree = setup_behavior_tree()
        logging.info("Tree structure:\n" + behavior_tree.tree_to_string())

        map_data = ''
        while True:
            current_line = sys.stdin.readline()
            if not current_line: break 
            if current_line.startswith("go"):
                state = PlanetWars(map_data)
                behavior_tree.execute(state)
                finish_turn() # Mandatory signal to Java [cite: 83, 85]
                
                for handler in logging.getLogger().handlers:
                    handler.flush()
                map_data = ''
            else:
                map_data += current_line
    except Exception as e:
        logging.exception("CRITICAL ERROR IN BT_BOT:")
