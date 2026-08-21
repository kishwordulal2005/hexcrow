#!/usr/bin/env python3

import os
import random
import sys
import time

for _stream in (sys.stdout, sys.stderr):
    if _stream and hasattr(_stream, 'reconfigure'):
        try:
            _stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

BANNERS = [
r'''
        .-.
       (o o)
       /|_|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Fall seven times,
  stand up eight."
       — Japanese proverb
''',

r'''
        .-.
       (• •)
      /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "This too shall pass."
       — Proverb
''',

r'''
        ___
      >(o o)>
       /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "He who has a why
  to live can bear
  almost any how."
       — Friedrich Nietzsche
''',

r'''
        .-.
       (o o)
      /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Turn your wounds
  into wisdom."
       — Oprah Winfrey
''',

r'''
        ___
       (o o)
       /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "The wound is the place
  where the Light enters you."
       — Rumi
''',

r'''
        .-.
      __(o o)__
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "We suffer more often
  in imagination than
  in reality."
       — Seneca
''',

r'''
        ___
      >(• •)>
       /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Difficulties strengthen
  the mind, as labor
  does the body."
       — Seneca
''',

r'''
        .-.
       (o o)
      /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Out of difficulties
  grow miracles."
       — Jean de La Bruyère
''',

r'''
        ___
       (• •)
      /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Adversity has the effect
  of eliciting talents
  which, in prosperous
  circumstances, would
  have lain dormant."
       — Horace
''',

r'''
        .-.
       (o o)
      /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Rock bottom became
  the solid foundation
  on which I rebuilt
  my life."
       — J.K. Rowling
''',

r'''
        ___
      __(o o)__
        /_\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "The only way out
  is through."
       — Robert Frost
''',

r'''
        .-.
       (o o)
       /|_|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Courage is resistance
  to fear, mastery
  of fear—not absence
  of fear."
       — Mark Twain
''',

r'''
        ___
       (• •)
       /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "I am not afraid
  of storms, for I am
  learning how to sail
  my ship."
       — Louisa May Alcott
''',

r'''
        .-.
      __(o o)__
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
 "Although the world
  is full of suffering,
  it is also full of
  the overcoming of it."
       — Helen Keller
''',

r'''
        ___
      >(o o)>
       /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Hope is a thing
   with feathers."
        — Emily Dickinson
''',

r'''
         .-.
        (o o)
        /|_|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Life does not have a
   rollback feature; you
   cannot undo a bad
   decision once run."
        — The System
''',

r'''
         ___
        (• •)
       /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "You cannot secure a
   system you do not
   understand; know
   yourself first."
        — The System
''',

r'''
         .-.
       __(o o)__
         /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Legacy code fails;
   update your mindset
   or be overrun by
   new realities."
        — The System
''',

r'''
         ___
       >(o o)>
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Garbage in,
   garbage out; the
   data you feed your
   mind is your output."
        — The System
''',

r'''
         .-.
        (o o)
       /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "The worst exploits
   come from inside
   your trusted
   network."
        — The System
''',

r'''
         ___
        (o o)
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Zero-day flaws live
   in everyone; life
   will find your
   vulnerability."
        — The System
''',

r'''
         .-.
        (• •)
       /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "An open port is an
   invitation; set
   boundaries or be
   exploited."
        — The System
''',

r'''
         ___
       __(o o)__
         /_\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "A quiet dashboard
   is not safety; the
   worst threats run
   in silence."
        — The System
''',

r'''
         .-.
        (o o)
        /|_|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Encrypt your inner
   thoughts; not all
   deserve raw access
   to you."
        — The System
''',

r'''
         ___
        (• •)
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "A backup plan is
   worthless if it has
   never been tested
   under pressure."
        — The System
''',

r'''
         .-.
       __(o o)__
         /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "You are the weakest
   link; your emotions
   bypass your logic
   every time."
        — The System
''',

r'''
         ___
       >(o o)>
        /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "An active attack is
   not stopped by
   pretending logs
   are clean."
        — The System
''',

r'''
         .-.
        (o o)
       /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Resilience is not
   avoiding the breach;
   it is staying up
   under fire."
        — The System
''',

r'''
         ___
        (• •)
       /|___|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Compromised assets
   must be isolated;
   you cannot heal in
   the toxic source."
        — The System
''',

r'''
         .-.
       __(o o)__
         /|\
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Trust is a fragile
   credential; once
   revoked, it takes a
   lifetime to rebuild."
        — The System
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "The crow watches in
   silence; patience is
   the oldest kind of power."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Crows remember every
   face that wronged them;
   never forget a hard lesson."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "A lone crow is a scout;
   solitude is where you
   read the terrain clearly."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "They call it a bad omen,
   but the crow only signals
   what is already true."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Dark wings, sharp eyes;
   adapt to the storm and
   you outlast the calm."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "The crow builds with what
   others discard; your scars
   are your sharpest tools."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Flight is earned, not given;
   every fall taught the wings
   the angle they needed."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "The flock is strength, but
   the wise crow still trusts
   its own beak first."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Noise scatters the flock;
   the quiet crow eats while
   the others panic."
        — The Murmur
''',

r'''
       \\
      (o>
   \_//)
    \_/_)
     _|_
╭──────────────╮
│  ● ONLINE ♡  │
╰──────────────╯
  "Omens do not kill;
   hesitation does. Move
   before the signal fades."
        — The Murmur
'''
]


def clear():
    
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    clear()
    print(random.choice(BANNERS))


def show_all(delay=2):
    for banner in BANNERS:
        clear()
        print(banner)
        time.sleep(delay)


if __name__ == "__main__":
    # Show a random banner
    show_banner()

    # Uncomment this instead if you want
    # all 40 banners to cycle:
    # show_all(3)