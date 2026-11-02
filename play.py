"""Play The Last Day Inn in the terminal.

    python3 play.py               # journal on
    python3 play.py --no-journal  # journal off (playtest condition)
"""

import sys

from engine import Game

LINE = "─" * 44


def ask(prompt):
    """input() that treats Ctrl+D / Ctrl+C (or the end of piped input) as quitting."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        return None


def main():
    game = Game(journal="--no-journal" not in sys.argv, log_dir="logs")
    print("\n" + game.opening + "\n")
    while not game.ended:
        print(LINE)
        print(game.observe())
        acts = game.actions()
        print()
        for i, a in enumerate(acts, 1):
            print("  %d. %s" % (i, game.describe_action(a)))
        choice = ask("\n> ")
        if choice is None or choice in ("q", "quit"):
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(acts):
            print("Type a number from the list, or q to quit.\n")
            continue
        action = acts[int(choice) - 1]
        label = game.describe_action(action).replace("✓ ", "")
        print("\n▶ You: %s\n" % label)
        print(game.act(action) + "\n")
    answer = ask("> ")
    if answer is None:
        return
    game.answer_end_prompt(answer)
    print("\nThanks for playing. Session log: %s" % game.log_path)


if __name__ == "__main__":
    main()
