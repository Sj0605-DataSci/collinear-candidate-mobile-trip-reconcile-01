"""
TripDesk: the local booking "app" (really a website opened in Chrome on the
emulator). Ground truth lives entirely in this server's SQLite DB -- the
verifier queries it directly (mirrors MobileWorld's own "backend database
verification" method), so there is no LLM-judge and no string matching.

BUILD-TIME/PRIVATE-ISH: this file itself IS shipped into the final image
(the agent needs it running to interact with the site at all -- unlike the
warehouse tasks' crate generator, there is no seed/answer hidden inside this
source, only a fixed catalog of options + whatever booking the agent makes).
The one thing that must stay out of the agent's reach is the *true required
constraint* (final return-by date, budget ceiling) -- that lives only in
private/scenario.json, read by the seed script and the verifier, never by
this server or any agent-visible file.
"""
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

DB_PATH = "/data/tripdesk.db"
_lock = threading.Lock()


def init_db(catalog):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY, route TEXT, depart_date TEXT, return_date TEXT,
        airline TEXT, price INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY, name TEXT, checkin_date TEXT, checkout_date TEXT,
        price_per_night INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, flight_id INTEGER, hotel_id INTEGER,
        confirmed_at TEXT, confirmed_real_t REAL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, text TEXT, real_t REAL)""")
    conn.execute("DELETE FROM flights")
    conn.execute("DELETE FROM hotels")
    conn.execute("DELETE FROM bookings")
    conn.execute("DELETE FROM messages")
    for f in catalog["flights"]:
        conn.execute("INSERT INTO flights (id, route, depart_date, return_date, airline, price) "
                     "VALUES (?,?,?,?,?,?)",
                     (f["id"], f["route"], f["depart_date"], f["return_date"], f["airline"], f["price"]))
    for h in catalog["hotels"]:
        conn.execute("INSERT INTO hotels (id, name, checkin_date, checkout_date, price_per_night) "
                     "VALUES (?,?,?,?,?)",
                     (h["id"], h["name"], h["checkin_date"], h["checkout_date"], h["price_per_night"]))
    conn.commit()
    conn.close()


PAGE_SHELL = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TripDesk</title><style>
body{{font-family:sans-serif;margin:0;padding:16px;font-size:20px;background:#fafafa}}
h1{{font-size:26px}} .card{{border:1px solid #ccc;border-radius:10px;padding:14px;margin:10px 0;background:#fff}}
button,a.btn{{display:inline-block;background:#1a73e8;color:#fff;padding:12px 18px;border-radius:8px;
text-decoration:none;border:none;font-size:18px;margin-top:8px}}
input{{font-size:20px;padding:8px;width:90%}}
.tag{{color:#555;font-size:16px}}
nav{{margin-bottom:14px}} nav a{{margin-right:14px;font-size:18px}}
.bubble{{max-width:75%;padding:10px 14px;border-radius:14px;margin:6px 0;font-size:19px}}
.bubble.them{{background:#e5e5ea;color:#000}}
.bubble.me{{background:#1a73e8;color:#fff;margin-left:auto;text-align:right}}
.bubblewrap{{display:flex}} .bubblewrap.me{{justify-content:flex-end}}
</style></head><body>
<nav><a href="/">Home</a><a href="/flights">Flights</a><a href="/hotels">Hotels</a>
<a href="/my-trip">My Trip</a><a href="/chat">Chat</a></nav>
{body}
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, html, code=200):
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        conn = self._conn()
        try:
            if path == "/":
                self._send(PAGE_SHELL.format(body="<h1>TripDesk</h1><p>Search and book your connecting trip.</p>"
                                                    "<a class='btn' href='/flights'>Search Flights</a> "
                                                    "<a class='btn' href='/hotels'>Search Hotels</a>"))
            elif path == "/flights":
                rows = conn.execute("SELECT id, route, depart_date, return_date, airline, price FROM flights "
                                     "ORDER BY price").fetchall()
                cards = ""
                for (fid, route, dep, ret, airline, price) in rows:
                    cards += (f"<div class='card'><b>{route}</b> ({airline})<br>"
                              f"<span class='tag'>Depart {dep} &rarr; Return {ret}</span><br>"
                              f"${price}<br><a class='btn' href='/book-flight?id={fid}'>Select</a></div>")
                self._send(PAGE_SHELL.format(body=f"<h1>Flights</h1>{cards}"))
            elif path == "/hotels":
                rows = conn.execute("SELECT id, name, checkin_date, checkout_date, price_per_night FROM hotels "
                                     "ORDER BY price_per_night").fetchall()
                cards = ""
                for (hid, name, ci, co, ppn) in rows:
                    cards += (f"<div class='card'><b>{name}</b><br>"
                              f"<span class='tag'>Check-in {ci} &rarr; Check-out {co}</span><br>"
                              f"${ppn}/night<br><a class='btn' href='/book-hotel?id={hid}'>Select</a></div>")
                self._send(PAGE_SHELL.format(body=f"<h1>Hotels</h1>{cards}"))
            elif path == "/book-flight":
                fid = int(qs["id"][0])
                conn.execute("INSERT INTO bookings (flight_id, hotel_id, confirmed_at) VALUES (?, NULL, NULL)",
                             (fid,))
                conn.commit()
                self._send(PAGE_SHELL.format(body="<h1>Flight selected</h1><p>Added to your trip.</p>"
                                                    "<a class='btn' href='/hotels'>Now choose a hotel</a> "
                                                    "<a class='btn' href='/my-trip'>View My Trip</a>"))
            elif path == "/book-hotel":
                hid = int(qs["id"][0])
                row = conn.execute("SELECT id FROM bookings WHERE hotel_id IS NULL ORDER BY id DESC LIMIT 1").fetchone()
                if row:
                    conn.execute("UPDATE bookings SET hotel_id=? WHERE id=?", (hid, row[0]))
                else:
                    conn.execute("INSERT INTO bookings (flight_id, hotel_id, confirmed_at) VALUES (NULL, ?, NULL)",
                                 (hid,))
                conn.commit()
                self._send(PAGE_SHELL.format(body="<h1>Hotel selected</h1><p>Added to your trip.</p>"
                                                    "<a class='btn' href='/my-trip'>Review &amp; Confirm</a>"))
            elif path == "/my-trip":
                row = conn.execute("SELECT id, flight_id, hotel_id, confirmed_at FROM bookings "
                                    "ORDER BY id DESC LIMIT 1").fetchone()
                if not row:
                    self._send(PAGE_SHELL.format(body="<h1>My Trip</h1><p>Nothing selected yet.</p>"))
                    return
                bid, fid, hid, confirmed = row
                flight = conn.execute("SELECT route, depart_date, return_date, airline, price FROM flights "
                                       "WHERE id=?", (fid,)).fetchone() if fid else None
                hotel = conn.execute("SELECT name, checkin_date, checkout_date, price_per_night FROM hotels "
                                      "WHERE id=?", (hid,)).fetchone() if hid else None
                body = "<h1>My Trip</h1>"
                if flight:
                    body += (f"<div class='card'>Flight: {flight[0]} ({flight[3]})<br>"
                              f"{flight[1]} &rarr; {flight[2]}<br>${flight[4]}</div>")
                else:
                    body += "<div class='card'>No flight selected yet.</div>"
                if hotel:
                    nights = 1
                    body += (f"<div class='card'>Hotel: {hotel[0]}<br>{hotel[1]} &rarr; {hotel[2]}<br>"
                              f"${hotel[3]}/night</div>")
                else:
                    body += "<div class='card'>No hotel selected yet.</div>"
                if confirmed:
                    body += "<div class='card'><b>CONFIRMED</b></div>"
                elif flight and hotel:
                    body += "<a class='btn' href='/confirm'>Confirm Booking</a>"
                self._send(PAGE_SHELL.format(body=body))
            elif path == "/confirm":
                row = conn.execute("SELECT id FROM bookings ORDER BY id DESC LIMIT 1").fetchone()
                if row:
                    conn.execute("UPDATE bookings SET confirmed_at=datetime('now'), confirmed_real_t=? WHERE id=?",
                                 (time.time(), row[0]))
                    conn.commit()
                self._send(PAGE_SHELL.format(body="<h1>Booked!</h1><p>Your trip is confirmed.</p>"))
            elif path == "/chat":
                rows = conn.execute("SELECT sender, text FROM messages ORDER BY id").fetchall()
                bubbles = ""
                for sender, text in rows:
                    cls = "me" if sender == "me" else "them"
                    bubbles += f"<div class='bubblewrap {cls}'><div class='bubble {cls}'>{text}</div></div>"
                self._send(PAGE_SHELL.format(body=f"<h1>Chat with Sam</h1>{bubbles}"))
            else:
                self._send("<h1>404</h1>", code=404)
        finally:
            conn.close()


def main():
    catalog = json.load(open("/app/private/catalog.json"))
    init_db(catalog)
    # bind 0.0.0.0 -- Chrome running inside the AVD guest reaches the host's
    # loopback via QEMU's NAT alias 10.0.2.2, not the container's own 127.0.0.1
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
