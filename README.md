# lemon-collector
Data that will be presented to lemonbar

# Warning not even remotely close to being usable!

Not as much hardcoded anymore, but still not fit for much.
Breaking api is more a rule than exception still...

Usage:
python main.py | lemonbar -p
for icons:
python main.py | lemonbar -p -f "Tamsyn-12" -f "FontAwesome-12"

Design ideas:

Designing some classes that could be inherited is probably a good idea.

Only thing that pops into mind regarding functions is a nice one to translate
each dict into something readable for lemonbar + positioning and order.

I would guess there is some need for a config file...

base:
    fg_color
    bg_color
    separation_marker
prehaps something for lemonbar if I'm not going to include it inside here that is:
    width
    height
    screen(s)
    font

objectA
    fg_color(A,B,C) depending on focus and what not.
    bg_color(A,B,C)
    padding_left
    padding_right
    position = (left, center, right)
    order = (numeric) # defines where it should be placed in each position where lowest number is furthest to the left.
and some object specific stuff like
    weather_site, weather_username, ...
    email_address, email_username, email_password

functions to expand:
bspwm
pacman

functions to add:
weather
cpu info (see if I can make a graph)
disk info
mem info

