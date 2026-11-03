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

Hide
Type "clear" Enter
Show

Type "python3 play.py" Sleep 400ms Enter
Sleep 3.5s

# Morning: open the drawer (old photo), go to the Lobby
Type "3" Enter
Sleep 2.5s
Type "1" Enter
Sleep 1.5s

# Afternoon: go to the Garden, show Mira the photo
Type "2" Enter
Sleep 1.5s
Type "6" Enter
Sleep 4s

# Evening and Night: back to the Lobby and wait by the clock
Type "1" Enter
Sleep 1.2s
Type "3" Enter
Sleep 1.2s
Type "3" Enter
Sleep 2.5s
Type "3" Enter
Sleep 7s

# Next morning: go down to the Lobby
Type "1" Enter
Sleep 7s
