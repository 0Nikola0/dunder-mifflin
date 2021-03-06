import sys
from src.settings import REQUIREMENTS

import os

if sys.version_info < (3, 8):
    sys.exit(
        "This game requires Python 3.8 or later."
    )

try:
    from src.game import Game
    from src.scenes.main_menu import MainMenu
except ImportError:
    import traceback
    traceback.print_exc()
    with open(REQUIREMENTS, "r") as f:
        req = f.read()
    sys.exit(
        f"""
Please ensure you have the following packages installed:

{req}
You can run 'pip install -r requirements.txt' to install these.
        """)

# Check environment variables
try:
    debug = int(os.environ['DEBUG'])
except KeyError:
    debug = 0

# Check args
if len(sys.argv) > 1:
    if sys.argv[1] == "--debug":
        debug = 1

if debug != 0:
    print("debugging")
    Game(debug=True).run()
else:
    # Let MainMenu make a selection then handle it
    selection = MainMenu().run()

    if selection == 'play':
        Game().run()
    elif selection == 'quit':
        pass  # just run off the end for now
