"""
Birthday Quest (Python / pygame)
Run:  pip install pygame-ce   then   python app.py   (do NOT use "streamlit run")
Mini Sudoku -> memory match -> geology quiz -> gift box
-> birthday cake (blow out the candles) -> letter + photo -> "reasons I love you" cards
"""
import math
import os
import random
import sys

import pygame

# ===================== EDIT THESE =====================
CONFIG = {
    "name": "Martin",
    # (label, color, message shown when matched)
    "pairs": [
        ("GEM", (60, 190, 230), "Rare, just like you"),
        ("PICK", (160, 110, 60), "You dig deep, in work and in love"),
        ("ROCK", (120, 120, 130), "Solid. Reliable. My favorite."),
        ("LAVA", (235, 90, 40), "You bring the heat!"),
    ],
    # (question, [options], index of correct option)
    "quiz": [
            ("“When is your birthday, handsome?", ["17", "18", "19","20"], 0),
            ("What is the hardest natural mineral?", ["Quartz", "Diamond", "Topaz"], 1),
            ("What's the best rock I've ever found?", ["A geode", "A fossil", "You"], 2),
            ("What's one thing I never want you to forget?", ["You're handsome and not old hehehe", "I love you more than you know", "All of these"], 2),
        ],
        "letter": (
            "You passed every level!\n\n"
            "Happy birthday to my favorite person in the whole world. :)"
            "You make my life so much brighter just by being in it.\n"
            " I'm so grateful to have you by my side,"
            " and I hope this new chapter of your life brings you all the happiness, love, and success you deserve. \n"
            " I'll always be here to support you, cheer you on, and love you through everything. \n"   
            "I love you more than words can say. \n\n"
            "Happy birthday, my love.  \n"
            "- Your favorite person"
    ),
    "photo": "us.png",          # put your photo next to this file with this name
    "caption": "My lovely, Martin",
    # tap-to-open cards on the last screen (4 fit best, 6 max)
    "reasons": [
        "You make me laugh every single day",
        "You take care of me, even when you're tired",
        "Every meal tastes better with you",
        "I can be completely myself around you",
    ],
}
# ======================================================

W, H = 480, 760
BG, INK, SOFT = (255, 233, 240), (58, 31, 61), (122, 90, 124)
ACC, GOLD, OK, WHITE = (255, 79, 120), (255, 183, 36), (47, 165, 107), (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Birthday Quest - Mini Sudoku")
clock = pygame.time.Clock()
FONTS = {s: pygame.font.Font(None, s) for s in (22, 24, 30, 38, 52)}


def wrap(s, size, maxw):
    lines = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if FONTS[size].size(t)[0] <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text(s, size, color, x, y, maxw=None, center=True):
    """Draw (wrapped) text; returns the y below it."""
    f = FONTS[size]
    for line in (wrap(s, size, maxw) if maxw else [s]):
        img = f.render(line, True, color)
        r = img.get_rect(center=(x, y + f.get_height() // 2)) if center else img.get_rect(topleft=(x, y))
        screen.blit(img, r)
        y += f.get_linesize()
    return y


class Button:
    def __init__(self, label, cx, cy, w=200, h=52, color=ACC):
        self.label, self.color = label, color
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)

    def draw(self, tc=WHITE):
        pygame.draw.rect(screen, (0, 0, 0, 40), self.rect.move(0, 4), border_radius=26)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=26)
        img = FONTS[30].render(self.label, True, tc)
        screen.blit(img, img.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ---------- state ----------
SCENES = ["sudoku", "memory", "quiz", "gift", "cake", "letter", "reasons"]
scene, G, pending = "sudoku", {}, None
particles = []
toast_msg, toast_until = "", 0
PHOTO = None
if CONFIG["photo"] and os.path.exists(CONFIG["photo"]):
    try:
        PHOTO = pygame.image.load(CONFIG["photo"]).convert()
    except pygame.error:
        PHOTO = None

B_START = Button("Start Sudoku", W // 2 - 90, 650, 170, 46)
B_RETRY = Button("Retry", W // 2, 470)
B_AGAIN = Button("Play again", W // 2, 712)
B_NEXT = Button("Continue", W // 2, 712)
B_BLOW = Button("Blow out the candles", W // 2, 610, 320, 56)
B_SUDOKU_RETRY = Button("Reset", 105, 728, 100, 38)
B_SUDOKU_SKIP = Button("Continue", 365, 728, 140, 38)
B_SUDOKU_CLEAR = Button("Clear", 240, 698, 90, 32, color=SOFT)


def now():
    return pygame.time.get_ticks()


def toast(msg):
    global toast_msg, toast_until
    toast_msg, toast_until = msg, now() + 1800


def burst(x, y, n=40):
    cols = [ACC, GOLD, (127, 224, 195), (143, 184, 255), WHITE, (199, 155, 255)]
    for i in range(n):
        a, s = random.random() * math.tau, random.uniform(2, 9)
        particles.append([x, y, math.cos(a) * s, math.sin(a) * s - 5, cols[i % 6], random.randint(40, 90)])


def go(name):
    global scene, G, pending
    scene, pending = name, None
    if name == "sudoku":
        # Easy 9x9 Sudoku. Zeroes are blank cells; givens cannot be edited.
        # Heart-shaped blank cells: only these cells are editable.
        # The puzzle remains easy because every other cell is given.
        solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        # Empty cells follow the pattern in your reference image.
        # A small heart is drawn in every empty cell until it is filled.
        heart_blanks = {
            (1, 1), (1, 2), (1, 3), (1, 5), (1, 6), (1, 7),
            (2, 0), (2, 4), (2, 8),
            (3, 0), (3, 8),
            (4, 0), (4, 8),
            (5, 1), (5, 7),
            (6, 2), (6, 6),
            (7, 3), (7, 5),
            (8, 4),
        }
        puzzle = [
            [0 if (r, c) in heart_blanks else solution[r][c] for c in range(9)]
            for r in range(9)
        ]
        G = dict(mode="ready", puzzle=[row[:] for row in puzzle], board=[row[:] for row in puzzle],
                 solution=solution, selected=None,
                 message="Fill blanks with 1–9. No repeats in any row, column, or 3×3 box.")
    elif name == "memory":
        cards = list(range(len(CONFIG["pairs"]))) * 2
        random.shuffle(cards)
        G = dict(cards=cards, up=set(), done=set(), open=[], lock=0)
    elif name == "quiz":
        G = dict(i=0, wrong=-1, wrong_until=0)
    elif name == "gift":
        G = dict(open=False, t0=0)
    elif name == "cake":
        G = dict(blown=False, t0=0)
    elif name == "reasons":
        G = dict(open=set())
    else:
        G = {}


def schedule(name, delay=900):
    global pending
    burst(W // 2, H // 2, 70)
    pending = (now() + delay, name)


# ---------- layout helpers ----------
def card_rect(i):
    col, row = i % 4, i // 4
    return pygame.Rect(30 + col * 108, 200 + row * 140, 96, 120)


def quiz_btn(i):
    qi = min(G["i"], len(CONFIG["quiz"]) - 1)  # stay valid while the next scene is loading
    return Button(CONFIG["quiz"][qi][1][i], W // 2, 380 + i * 70, 400, 54, WHITE)


GIFT_RECT = pygame.Rect(150, 400, 180, 130)


def reason_rect(i):
    return pygame.Rect(W // 2 - 208 + (i % 2) * 216, 170 + (i // 2) * 190, 200, 174)


# ---------- easy Sudoku (9x9, 3x3 boxes) ----------
SUDOKU_X, SUDOKU_Y, SUDOKU_SQ = 60, 190, 40


def sudoku_cell_at(pos):
    x, y = pos
    col, row = (x - SUDOKU_X) // SUDOKU_SQ, (y - SUDOKU_Y) // SUDOKU_SQ
    if 0 <= row < 9 and 0 <= col < 9:
        return int(row), int(col)
    return None


def sudoku_number_button(n):
    col, row = (n - 1) % 3, (n - 1) // 3
    return Button(str(n), 120 + col * 120, 578 + row * 38, 38, 34)


def sudoku_is_valid(board, row, col, value):
    if any(board[row][c] == value for c in range(9) if c != col):
        return False
    if any(board[r][col] == value for r in range(9) if r != row):
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if (r, c) != (row, col) and board[r][c] == value:
                return False
    return True


def sudoku_check_complete():
    if all(all(value != 0 for value in row) for row in G["board"]):
        if G["board"] == G["solution"]:
            G["mode"] = "won"
            G["message"] = "Perfect! You solved the Sudoku!"
            toast("Puzzle solved! ❤️")
            schedule("memory", 1500)
        else:
            G["message"] = "All cells filled, but some numbers are wrong. Try again!"


# ---------- events ----------
def handle(e):
    if e.type == pygame.MOUSEMOTION and scene == "catch":
        G["tx"] = e.pos[0]
    if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
        return
    p = e.pos
    if scene == "sudoku":
        if G["mode"] == "ready" and B_START.hit(p):
            G["mode"] = "play"
            G["message"] = "Click a blank cell, then select a number 1–9."
        elif B_SUDOKU_SKIP.hit(p) and G["mode"] in ("ready", "play", "won"):
            go("memory")
        elif B_SUDOKU_RETRY.hit(p) and G["mode"] in ("play", "won"):
            go("sudoku")
        elif G["mode"] == "play":
            cell = sudoku_cell_at(p)
            if cell is not None:
                r, c = cell
                if G["puzzle"][r][c] == 0:
                    G["selected"] = cell
            else:
                if G["selected"] is not None:
                    for n in range(1, 10):
                        if sudoku_number_button(n).hit(p):
                            r, c = G["selected"]
                            if sudoku_is_valid(G["board"], r, c, n):
                                G["board"][r][c] = n
                                G["message"] = "Nice! Keep going."
                                sudoku_check_complete()
                            else:
                                toast("No repeats in a row, column, or 3x3 box!")
                            break
                if B_SUDOKU_CLEAR.hit(p) and G["selected"] is not None:
                    r, c = G["selected"]
                    G["board"][r][c] = 0
        return
    if scene == "catch":
        G["tx"] = p[0]
        if G["mode"] == "ready" and B_START.hit(p):
            G["mode"] = "play"
        elif G["mode"] == "lose" and B_RETRY.hit(p):
            go("catch")
            G["mode"] = "play"
    elif scene == "memory" and not pending and now() >= G["lock"]:
        for i in range(len(G["cards"])):
            if card_rect(i).collidepoint(p) and i not in G["up"] and i not in G["done"]:
                G["up"].add(i)
                G["open"].append(i)
                if len(G["open"]) == 2:
                    a, b = G["open"]
                    if G["cards"][a] == G["cards"][b]:
                        G["done"] |= {a, b}
                        toast(CONFIG["pairs"][G["cards"][a]][2])
                        G["open"] = []
                        if len(G["done"]) == len(G["cards"]):
                            schedule("quiz")
                    else:
                        G["lock"] = now() + 800
                break
    elif scene == "quiz" and not pending and now() >= G["wrong_until"]:
        for i in range(3):
            if quiz_btn(i).hit(p):
                if i == CONFIG["quiz"][G["i"]][2]:
                    toast("Correct!")
                    G["i"] += 1
                    if G["i"] >= len(CONFIG["quiz"]):
                        schedule("gift")
                else:
                    G["wrong"], G["wrong_until"] = i, now() + 500
                    toast("Hmm, are you sure?")
    elif scene == "gift" and not G["open"] and GIFT_RECT.inflate(40, 80).collidepoint(p):
        G["open"], G["t0"] = True, now()
        burst(W // 2, 420, 90)
    elif scene == "cake" and not G["blown"] and B_BLOW.hit(p):
        G["blown"], G["t0"] = True, now()
        for x in (W // 2 - 80, W // 2, W // 2 + 80):
            burst(x, 260, 30)
        schedule("letter", 1900)
    elif scene == "letter" and B_NEXT.hit(p):
        go("reasons")
    elif scene == "reasons":
        for i in range(len(CONFIG["reasons"])):
            if reason_rect(i).collidepoint(p) and i not in G["open"]:
                G["open"].add(i)
                burst(*reason_rect(i).center, 18)
        if B_AGAIN.hit(p):
            go("sudoku")


# ---------- update ----------
def update(dt):
    global pending
    for p in particles:
        p[3] += 0.25
        p[0] += p[2]
        p[1] += p[3]
        p[2] *= 0.99
        p[5] -= 1
    particles[:] = [p for p in particles if p[5] > 0]

    if pending and now() >= pending[0]:
        go(pending[1])
        return

    if scene == "catch" and G["mode"] == "play":
        k = pygame.key.get_pressed()
        if k[pygame.K_LEFT]:
            G["tx"] -= 0.5 * dt
        if k[pygame.K_RIGHT]:
            G["tx"] += 0.5 * dt
        G["px"] += (G["tx"] - G["px"]) * min(1, 0.02 * dt)
        G["px"] = max(40, min(W - 40, G["px"]))
        G["spawn"] -= dt
        if G["spawn"] <= 0:
            r = random.random()
            kind = "gem" if r < 0.62 else "star" if r < 0.82 else "lava"
            G["items"].append([random.randint(30, W - 30), -20, random.uniform(0.15, 0.25), kind])
            G["spawn"] = max(420, 800 - G["score"] * 20)
        for it in G["items"][:]:
            it[1] += it[2] * dt
            if H - 110 < it[1] < H - 65 and abs(it[0] - G["px"]) < 46:
                G["items"].remove(it)
                if it[3] == "lava":
                    G["lives"] -= 1
                    burst(it[0], it[1], 14)
                else:
                    G["score"] += 3 if it[3] == "star" else 1
                    burst(it[0], it[1], 12)
                    if it[3] == "star":
                        toast(CONFIG["notes"][G["ni"] % len(CONFIG["notes"])])
                        G["ni"] += 1
                if G["lives"] <= 0:
                    G["mode"] = "lose"
                elif G["score"] >= CONFIG["catch_target"]:
                    G["mode"] = "won"
                    toast("Level 1 complete!")
                    schedule("memory")
            elif it[1] > H + 30:
                G["items"].remove(it)

    if scene == "memory" and G["lock"] and now() >= G["lock"]:
        for i in G["open"]:
            G["up"].discard(i)
        G["open"], G["lock"] = [], 0

    if scene == "gift" and G["open"] and now() - G["t0"] > 1300 and not pending:
        go("cake")
        burst(W * 0.25, 250, 50)
        burst(W * 0.75, 250, 50)


# ---------- drawing ----------
def draw_dots():
    cur = SCENES.index(scene)
    for k in range(5):
        c = ACC if k < cur else GOLD if k == cur else (225, 200, 210)
        pygame.draw.circle(screen, c, (W // 2 - 60 + k * 30, 26), 8 if k == cur else 6)


def draw_item(x, y, kind):
    if kind == "gem":
        pts = [(x, y - 17), (x + 14, y), (x, y + 17), (x - 14, y)]
        pygame.draw.polygon(screen, (90, 220, 255), pts)
        pygame.draw.polygon(screen, WHITE, pts, 2)
    elif kind == "star":
        pts = [(x + math.cos(-math.pi / 2 + i * math.pi / 5) * (18 if i % 2 == 0 else 8),
                y + math.sin(-math.pi / 2 + i * math.pi / 5) * (18 if i % 2 == 0 else 8)) for i in range(10)]
        pygame.draw.polygon(screen, GOLD, pts)
    else:
        pygame.draw.circle(screen, (200, 50, 30), (int(x), int(y)), 16)
        pygame.draw.circle(screen, (255, 150, 40), (int(x), int(y)), 8)


def panel(h=300):
    r = pygame.Rect(0, 0, 380, h)
    r.center = (W // 2, 420)
    pygame.draw.rect(screen, WHITE, r, border_radius=22)
    return r


def draw_catch():
    text("Level 1: Mine the gems", 38, INK, W // 2, 52)
    text(f"{G['score']}/{CONFIG['catch_target']}      Lives: {G['lives']}", 30, SOFT, W // 2, 90)
    for x, y, _, kind in G["items"]:
        draw_item(x, y, kind)
    px = G["px"]
    pygame.draw.polygon(screen, (150, 100, 60), [(px - 40, H - 100), (px + 40, H - 100), (px + 30, H - 60), (px - 30, H - 60)])
    pygame.draw.rect(screen, (110, 70, 40), (px - 44, H - 106, 88, 10), border_radius=4)
    if G["mode"] == "ready":
        r = panel(330)
        text("Mine the gems", 38, INK, W // 2, r.top + 30)
        text("Move the mouse (or use arrow keys). Catch gems and stars. Dodge lava!", 24, SOFT, W // 2, r.top + 85, 320)
        text("Gem +1    Star +3 and a love note", 24, INK, W // 2, r.top + 170)
        B_START.draw()
    elif G["mode"] == "lose":
        r = panel(260)
        text("Too much lava!", 38, INK, W // 2, r.top + 40)
        text("Back to the rig. Try again.", 24, SOFT, W // 2, r.top + 100)
        B_RETRY.draw()


def draw_sudoku():
    text("Easy Sudoku", 38, INK, W // 2, 58)
    text("9×9 board · numbers 1–9", 24, SOFT, W // 2, 96)
    text(G.get("message", ""), 22, INK, W // 2, 135, 440)
    board = G["board"]
    for r in range(9):
        for c in range(9):
            rect = pygame.Rect(SUDOKU_X + c * SUDOKU_SQ, SUDOKU_Y + r * SUDOKU_SQ,
                               SUDOKU_SQ, SUDOKU_SQ)
            base = (255, 255, 255) if (r + c) % 2 == 0 else (250, 238, 244)
            if G["selected"] == (r, c):
                base = (255, 225, 145)
            pygame.draw.rect(screen, base, rect)
            if board[r][c]:
                color = INK if G["puzzle"][r][c] else ACC
                img = FONTS[30].render(str(board[r][c]), True, color)
                screen.blit(img, img.get_rect(center=rect.center))
            else:
                # Cute little heart marks each empty cell until a number is entered.
                draw_heart(rect.centerx, rect.centery - 2, 6, (235, 155, 190))
            pygame.draw.rect(screen, (205, 170, 190), rect, 1)
    # Thick lines mark the 3x3 boxes.
    for i in (0, 3, 6, 9):
        x = SUDOKU_X + i * SUDOKU_SQ
        y = SUDOKU_Y + i * SUDOKU_SQ
        width = 4 if i in (0, 9) else 3
        pygame.draw.line(screen, INK, (x, SUDOKU_Y), (x, SUDOKU_Y + 9 * SUDOKU_SQ), width)
        pygame.draw.line(screen, INK, (SUDOKU_X, y), (SUDOKU_X + 9 * SUDOKU_SQ, y), width)
    if G["mode"] == "ready":
        text("Rules: no repeated numbers in each row, column, or 3×3 box.", 22, SOFT, W // 2, 565, 440)
        B_START.draw()
        B_SUDOKU_SKIP.draw()
    elif G["mode"] == "play":
        for n in range(1, 10):
            sudoku_number_button(n).draw()
        B_SUDOKU_CLEAR.draw()
        B_SUDOKU_RETRY.draw()
        B_SUDOKU_SKIP.draw()
    elif G["mode"] == "won":
        text("Solved! Your next surprise is ready!", 24, ACC, W // 2, 565, 440)
        B_SUDOKU_SKIP.draw()


def draw_memory():
    text("Level 2: Match the specimens", 38, INK, W // 2, 70)
    text("Flip the cards and find the pairs.", 24, SOFT, W // 2, 110)
    for i, c in enumerate(G["cards"]):
        r = card_rect(i)
        if i in G["up"] or i in G["done"]:
            label, color, _ = CONFIG["pairs"][c]
            pygame.draw.rect(screen, WHITE, r, border_radius=14)
            pygame.draw.rect(screen, OK if i in G["done"] else color, r, 4, border_radius=14)
            text(label, 30, color, r.centerx, r.centery - 10)
        else:
            pygame.draw.rect(screen, ACC, r, border_radius=14)
            text("?", 52, WHITE, r.centerx, r.centery - 16)


def draw_quiz():
    q, opts, _ = CONFIG["quiz"][min(G["i"], len(CONFIG["quiz"]) - 1)]
    text("Level 3: Geologist final exam", 38, INK, W // 2, 70)
    text(f"Question {min(G['i'] + 1, len(CONFIG['quiz']))} of {len(CONFIG['quiz'])}", 24, SOFT, W // 2, 120)
    text(q, 38, INK, W // 2, 200, 400)
    for i in range(3):
        b = quiz_btn(i)
        if G["wrong"] == i and now() < G["wrong_until"]:
            b.color = (255, 120, 120)
        b.draw(INK)


def draw_gift():
    text("You did it!", 52, INK, W // 2, 140)
    text("Click the box to open your gift.", 30, SOFT, W // 2, 205)
    bob = 0 if G["open"] else math.sin(now() / 250) * 6
    base = GIFT_RECT.move(0, bob + 20)
    pygame.draw.rect(screen, ACC, base, border_radius=6)
    pygame.draw.rect(screen, GOLD, (base.centerx - 13, base.top, 26, base.height))
    t = min(1, (now() - G["t0"]) / 600) if G["open"] else 0
    lid = pygame.Rect(base.left - 8 + t * 90, base.top - 38 - t * 120, base.width + 16, 44)
    pygame.draw.rect(screen, ACC, lid, border_radius=6)
    pygame.draw.rect(screen, GOLD, (lid.centerx - 13, lid.top, 26, lid.height))


def draw_letter():
    text(f"Happy Birthday, {CONFIG['name']}!", 38, ACC, W // 2, 40)
    y = text(CONFIG["letter"], 24, INK, 30, 85, 420, center=False)
    top = y + 40  # the white frame sticks out 25px above the photo box, so leave room
    h = max(140, min(285, 636 - top))  # shrink the photo if the letter is long
    box = pygame.Rect(0, 0, min(230, int(h * 0.81)), h)
    box.midtop = (W // 2, top)
    pygame.draw.rect(screen, WHITE, box.inflate(16, 50), border_radius=6)
    pygame.draw.rect(screen, (230, 215, 225), box.inflate(16, 50), 2, border_radius=6)
    if PHOTO:
        iw, ih = PHOTO.get_size()
        s = min(box.w / iw, box.h / ih)
        img = pygame.transform.smoothscale(PHOTO, (int(iw * s), int(ih * s)))
        screen.blit(img, img.get_rect(center=box.center))
    else:
        pygame.draw.rect(screen, (205, 182, 220), box, 2, border_radius=4)
        text("Put your photo here:", 24, SOFT, box.centerx, box.centery - 30)
        text(f"save it as {CONFIG['photo']}", 24, SOFT, box.centerx, box.centery)
        text("next to this file", 24, SOFT, box.centerx, box.centery + 26)
    text(CONFIG["caption"], 30, INK, W // 2, box.bottom + 14)
    B_NEXT.draw()


def draw_cake():
    text("Happy Birthday,", 52, INK, W // 2, 62)
    text(CONFIG["name"] + "!", 52, ACC, W // 2, 104)
    text("There's a little gift waiting. Blow out the candles first!", 24, SOFT, W // 2, 152, 400)
    S, ox, oy = 1.25, (W - 325) // 2, 215

    def R(x, y, w, h):
        return pygame.Rect(ox + x * S, oy + y * S, w * S, h * S)

    def P(x, y):
        return (ox + x * S, oy + y * S)

    cream = (255, 244, 234)
    pygame.draw.ellipse(screen, (232, 212, 222), R(10, 214, 240, 28))
    pygame.draw.rect(screen, (255, 143, 163), R(30, 150, 200, 74), border_radius=14)
    pygame.draw.rect(screen, ACC, R(30, 150, 200, 74), 3, border_radius=14)
    pygame.draw.rect(screen, (255, 208, 220), R(50, 108, 160, 50), border_radius=12)
    pygame.draw.rect(screen, cream, R(50, 108, 160, 16), border_radius=8)
    for i in range(8):
        pygame.draw.circle(screen, cream, P(60 + i * 20, 124), int(10 * S * 0.8))
    for x, y in ((75, 188), (130, 196), (185, 188)):
        pygame.draw.circle(screen, cream, P(x, y), int(6 * S))
    since = now() - G["t0"]
    for i, (cx_, top, h, col) in enumerate(
        [(93, 66, 44, (127, 224, 195)), (130, 58, 52, GOLD), (167, 66, 44, (143, 184, 255))]
    ):
        pygame.draw.rect(screen, col, R(cx_ - 5, top, 10, h), border_radius=3)
        if not G["blown"]:  # flickering flame
            f = math.sin(now() / 90 + i * 2)
            pts = [P(cx_ - 6, top - 3), P(cx_ - 7, top - 14), P(cx_ + f * 2, top - 3 - 26 * (1 + 0.08 * f)),
                   P(cx_ + 7, top - 14), P(cx_ + 6, top - 3)]
            pygame.draw.polygon(screen, GOLD, pts)
            pygame.draw.circle(screen, (255, 236, 160), P(cx_, top - 9), int(3.5 * S))
        elif since < 1600:  # smoke fades out as it rises
            t = since / 1600
            c = tuple(int(a + (b - a) * t) for a, b in zip((169, 155, 181), BG))
            pygame.draw.circle(screen, c, P(cx_ + math.sin(t * 6 + i) * 3, top - 12 - 30 * t), 5)
    if G["blown"]:
        text("Make a wish!", 38, ACC, W // 2, 610)
    else:
        B_BLOW.draw()


def draw_heart(cx_, cy_, s, color):
    pygame.draw.circle(screen, color, (cx_ - s // 2, cy_ - s // 4), s // 2 + 1)
    pygame.draw.circle(screen, color, (cx_ + s // 2, cy_ - s // 4), s // 2 + 1)
    pygame.draw.polygon(screen, color, [(cx_ - s - 1, cy_ - s // 8), (cx_ + s + 1, cy_ - s // 8), (cx_, cy_ + s)])


def draw_reasons():
    text("Reasons I love you", 38, INK, W // 2, 60)
    text("Tap a card to open it", 24, SOFT, W // 2, 108)
    for i, reason in enumerate(CONFIG["reasons"]):
        r = reason_rect(i)
        if i in G["open"]:
            pygame.draw.rect(screen, WHITE, r, border_radius=16)
            h = len(wrap(reason, 24, 170)) * FONTS[24].get_linesize()
            text(reason, 24, INK, r.centerx, r.centery - h // 2, 170)
        else:
            pygame.draw.rect(screen, (255, 214, 226), r, border_radius=16)
            draw_heart(r.centerx, r.centery - 22, 14, ACC)
            text("Tap to open", 24, INK, r.centerx, r.centery + 16)
    text("Made with love", 30, SOFT, W // 2, 640)
    B_AGAIN.draw()


def draw():
    screen.fill(BG)
    if scene in SCENES[:5]:
        draw_dots()
    {"sudoku": draw_sudoku, "memory": draw_memory, "quiz": draw_quiz, "gift": draw_gift,
     "cake": draw_cake, "letter": draw_letter, "reasons": draw_reasons}[scene]()
    for x, y, _, _, c, life in particles:
        pygame.draw.rect(screen, c, (x, y, 7, 5))
    if now() < toast_until:
        img = FONTS[30].render(toast_msg, True, INK)
        r = img.get_rect(center=(W // 2, 54 if scene != "catch" else 130)).inflate(30, 18)
        pygame.draw.rect(screen, WHITE, r, border_radius=20)
        screen.blit(img, img.get_rect(center=r.center))
    pygame.display.flip()


def main():
    go("sudoku")
    while True:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            handle(e)
        update(dt)
        draw()


if __name__ == "__main__":
    main()