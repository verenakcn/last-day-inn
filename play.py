"""Play The Last Day Inn in the terminal.

    python3 play.py               # journal on
    python3 play.py --no-journal  # journal off (playtest condition)
"""

import sys

from engine import Game


def main():
    game = Game(journal="--no-journal" not in sys.argv, log_dir="logs")
    print("\n" + game.opening + "\n")
    while not game.ended:
        print(game.observe())
        acts = game.actions()
        print()
        for i, a in enumerate(acts, 1):
            print("  %d. %s" % (i, game.describe_action(a)))
        choice = input("\n> ").strip()
        if choice in ("q", "quit"):
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(acts):
            print("Type a number from the list, or q to quit.\n")
            continue
        print("\n" + game.act(acts[int(choice) - 1]) + "\n")
    game.answer_end_prompt(input("> ").strip())
    print("\nThanks for playing. Session log: %s" % game.log_path)


if __name__ == "__main__":
    main()
