"""Play The Last Day Inn in the terminal.

    python3 play.py               # journal on
    python3 play.py --no-journal  # journal off (playtest condition)
"""

import re
import sys

from engine import Game

LINE = "─" * 44
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)


def show(text):
    """**marked** lines from world.json print in bold in a terminal, plain otherwise."""
    print(BOLD.sub(r"\033[1m\1\033[0m" if sys.stdout.isatty() else r"\1", text))


def menu(game, acts):
    """Actions grouped under Go / Look / Show, numbered in the engine's order."""
    groups = {}
    for i, a in enumerate(acts, 1):
        groups.setdefault(a.partition(":")[0], []).append("%d. %s" % (i, game.describe_action(a, short=True)))
    lines = [game.ui["menu_prompt"]]
    for verb, key in (("move", "group_move"), ("examine", "group_examine"), ("present", "group_present")):
        if verb in groups:  # several items per line; an item never splits across lines
            line = "  %-6s " % game.ui[key]
            for item in groups[verb]:
                if line.strip() not in ("", game.ui[key]) and len(line) + len(item) > 72:
                    lines.append(line.rstrip())
                    line = " " * 9
                line += item + "   "
            lines.append(line.rstrip())
    return "\n".join(lines)


def ask(prompt):
    """input() that treats Ctrl+D / Ctrl+C (or the end of piped input) as quitting."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        return None


def main():
    game = Game(journal="--no-journal" not in sys.argv, log_dir="logs")
    show("\n" + game.opening + "\n")
    while not game.ended:
        if not game.interlude:  # a line between turns; after a banner it would only repeat it
            print(LINE)
        show(game.observe())
        acts = game.actions()
        print("\n" + LINE)
        print(menu(game, acts))
        choice = ask("\n> ")
        if choice is None or choice in ("q", "quit"):
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(acts):
            print("Type a number from the list, or q to quit.\n")
            continue
        action = acts[int(choice) - 1]
        label = game.describe_action(action).replace("✓ ", "")
        print("\n▶ You: %s\n" % label)
        game.act(action)
        if game.interlude:
            show(game.interlude + "\n")
    answer = ask("> ")
    if answer is None:
        return
    game.answer_end_prompt(answer)
    print("\nThanks for playing. Session log: %s" % game.log_path)


if __name__ == "__main__":
    main()
