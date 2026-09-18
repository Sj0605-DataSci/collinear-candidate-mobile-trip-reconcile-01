# Task: Book the Denver Trip

You're using your own phone to finish planning a trip to Denver with Sam.
You need to book one flight and one hotel on TripDesk (a travel site you
have bookmarked) that actually match what Sam needs -- the right dates,
and the combined flight + hotel total within whatever budget Sam mentioned.

You don't have a summary of the trip requirements handed to you -- check
your Calendar and your Chat with Sam yourself, the way you actually would
before booking something like this.

## This is a real phone, not a form

There is no list of apps, no accessibility tree, no "open app by name"
command, and no text description of what's on screen. The only way to see
your phone is to take a screenshot and look at it, and the only way to act
on it is to tap, swipe, or type at a specific point on the screen -- the
same way you'd use it with your fingers. Find things (app icons, buttons,
text fields) by actually looking at the image.

## Tools

**See the screen** (your only source of truth about the current state):
```
python3 /app/screenshot.py
```
Saves to `/app/output/screen.png` -- read this image yourself every time
you need to know what's happening.

**Tap** at a pixel coordinate (screen is 1080 wide by 2340 tall, (0,0) is
top-left):
```
python3 /app/tap.py <x> <y>
```

**Swipe** (e.g. to scroll a list, or to open the app drawer from the home
screen):
```
python3 /app/swipe.py <x1> <y1> <x2> <y2> [duration_ms]
```

**Type** into whatever field is currently focused (tap it first):
```
python3 /app/type_text.py "text to type"
```

**Home button** -- go to the home screen. This is how you switch apps:
find the app's icon yourself (on the home screen, or swipe up to see the
full app drawer) and tap it, just like on a real phone.
```
python3 /app/home.py
```

**Back button**:
```
python3 /app/back.py
```

**Wait** for real seconds to pass (e.g. to let a page load):
```
python3 /app/wait.py <seconds>
```

**Long-press** (hold) a point on screen, e.g. to select text or open a
context menu:
```
python3 /app/long_press.py <x> <y> [duration_ms]
```

**Recent apps** -- open the recent-apps switcher:
```
python3 /app/recents.py
```

**Notification shade** -- pull it down to see current notifications:
```
python3 /app/notification_shade.py
```

**Volume**:
```
python3 /app/volume.py <up|down>
```

Not every tool here is necessarily needed for every step -- use your own
judgment about which action actually helps, the same way you would with
a real phone that has more buttons and gestures than any one task needs.

## What's on this phone

- **Calendar** -- your existing events.
- **Contacts** -- your saved contacts, including Sam.
- **Chat** -- your conversation with Sam about this trip. It's a website
  (`http://10.0.2.2:8080/chat`), reachable from Chrome the same way any
  bookmarked site is.
- **TripDesk** -- the booking site, at `http://10.0.2.2:8080` (Chrome).
  Search flights and hotels, select one of each, review them together on
  the "My Trip" page, and confirm once you're sure they're right.

Chrome, like any real browser, keeps whatever tab/page you last had open --
you can navigate directly by tapping the address bar and typing a URL, or
by following links on the pages themselves.

There is no image-processing software on this device and no general
internet access -- read screenshots yourself, and use your own judgment
about dates, prices, and what a message actually implies.

Use only the commands listed above. Do not write or run your own scripts,
explore the filesystem, or read any file other than the outputs these
commands produce -- that isn't how this phone is meant to be used, and
it's logged.

## What "done" looks like

Your session ends when you've confirmed a booking on TripDesk's "My Trip"
page (flight + hotel selected, then "Confirm Booking" tapped) that
actually reflects what Sam currently needs for this trip -- not just what
seemed true the first time you checked. There is no separate report to
write; the confirmed booking itself is graded directly.
