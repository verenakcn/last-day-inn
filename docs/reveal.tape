# The reveal path in The Last Day Inn: photo → Mira, midnight in the Lobby, wake, "You still haven't tried the pie."
# Record from the repo root: vhs docs/reveal.tape (needs vhs: brew install vhs)

Output docs/reveal.gif

Set Shell "bash"
Set FontSize 15
Set Width 1420
Set Height 820
Set Padding 24
Set TypingSpeed 70ms
Set Theme "Catppuccin Mocha"

# Hidden: launch, open the drawer (old photo), go through the Lobby to the Garden
Hide
Type "clear" Enter
Type "python3 play.py" Enter
Sleep 1s
Type "3" Enter
Type "1" Enter
Type "2" Enter
Sleep 1s
Show

# First frame: the Garden, Mira's pie line, the photo in the journal
Sleep 2.2s

# Show Mira the photo
Type "6" Enter
Sleep 3.5s

# Evening and Night: back to the Lobby and wait by the clock
Type "1" Enter
Sleep 1s
Type "3" Enter
Sleep 1s
Type "3" Enter
Sleep 1.8s
Type "3" Enter
Sleep 4.2s

# Next morning: go down to the Lobby
Type "1" Enter
Sleep 4.5s
