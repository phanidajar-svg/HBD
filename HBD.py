import random
import streamlit as st
from pathlib import Path

# ---------------- Birthday Quest: Streamlit edition ----------------
st.set_page_config(page_title="Birthday Quest 💗", page_icon="💗", layout="centered", initial_sidebar_state="collapsed")

CONFIG = {
    "name": "Martin",
    "pairs": [
        ("GEM", "Rare, just like you", "💎"),
        ("PICK", "You dig deep, in work and in love", "⛏️"),
        ("ROCK", "Solid. Reliable. My favorite.", "🪨"),
        ("LAVA", "You bring the heat!", "🌋"),
    ],
    "quiz": [
        ("When is your birthday, handsome?", ["17", "18", "19", "20"], 0),
        ("What is the hardest natural mineral?", ["Quartz", "Diamond", "Topaz"], 1),
        ("What's the best rock I've ever found?", ["A geode", "A fossil", "You"], 2),
        ("What's one thing I never want you to forget?", [
            "You're handsome and not old hehehe",
            "I love you more than you know",
            "All of these"
        ], 2),
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
    "photo": "us.png",
    "caption": "My lovely, Martin",
    "reasons": [
        "You make me laugh every single day",
        "You take care of me, even when you're tired",
        "Every meal tastes better with you",
        "I can be completely myself around you",
    ],
}

BG = "#ffe9f0"
INK = "#3a1f3d"
ACC = "#ff4f78"
SOFT = "#7a5a7c"

st.markdown(f"""
<style>
.stApp {{ background: {BG}; color: {INK}; }}
.block-container {{ max-width: 760px; padding-top: 1.5rem; padding-bottom: 3rem; }}
h1, h2, h3, p, label {{ color: {INK} !important; }}
div.stButton > button {{
  border-radius: 18px; border: 1px solid #f5b7cc; background: #ff4f78;
  color: white; font-weight: 650; min-height: 2.7rem;
}}
div.stButton > button:hover {{ background: #e63e68; color: white; border-color: #e63e68; }}
div[data-testid="stRadio"] label {{ color: {INK} !important; }}
.heart-title {{ text-align:center; color:{ACC}; font-size: 2.4rem; font-weight:800; }}
.subtitle {{ text-align:center; color:{SOFT}; font-size:1.1rem; }}
.sudoku-wrap {{ display:flex; justify-content:center; }}
.sudoku {{ border-collapse:collapse; margin: 0 auto; }}
.sudoku td {{ width:36px; height:36px; text-align:center; border:1px solid #cda9bb; font-weight:700; }}
</style>
""", unsafe_allow_html=True)

SOLUTION = [
    [5,3,4,6,7,8,9,1,2],
    [6,7,2,1,9,5,3,4,8],
    [1,9,8,3,4,2,5,6,7],
    [8,5,9,7,6,1,4,2,3],
    [4,2,6,8,5,3,7,9,1],
    [7,1,3,9,2,4,8,5,6],
    [9,6,1,5,3,7,2,8,4],
    [2,8,7,4,1,9,6,3,5],
    [3,4,5,2,8,6,1,7,9],
]
# These blank locations form a small heart-like pattern on the board.
HEART_BLANKS = {
    (1,1), (1,2), (1,3), (1,5), (1,6), (1,7),
    (2,0), (2,4), (2,8),
    (3,0), (3,8),
    (4,0), (4,8),
    (5,1), (5,7),
    (6,2), (6,6),
    (7,3), (7,5),
    (8,4),
}
PUZZLE = [[0 if (r,c) in HEART_BLANKS else SOLUTION[r][c] for c in range(9)] for r in range(9)]

def init_state():
    defaults = {
        "scene": "sudoku", "sudoku_started": False,
        "sudoku_board": [row[:] for row in PUZZLE], "sudoku_selected": None,
        "memory_cards": [], "memory_flipped": [], "memory_matched": [],
        "quiz_i": 0, "gift_open": False, "candles_blown": False,
        "opened_reasons": set(), "last_message": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def go(scene):
    st.session_state.scene = scene
    st.session_state.last_message = ""
    if scene == "sudoku":
        st.session_state.sudoku_started = False
        st.session_state.sudoku_board = [row[:] for row in PUZZLE]
        st.session_state.sudoku_selected = None
    elif scene == "memory":
        cards = list(range(len(CONFIG["pairs"]))) * 2
        random.shuffle(cards)
        st.session_state.memory_cards = cards
        st.session_state.memory_flipped = []
        st.session_state.memory_matched = []
    elif scene == "quiz":
        st.session_state.quiz_i = 0
    elif scene == "gift":
        st.session_state.gift_open = False
    elif scene == "cake":
        st.session_state.candles_blown = False
    elif scene == "reasons":
        st.session_state.opened_reasons = set()

def sudoku_valid(board, row, col, value):
    if any(board[row][c] == value for c in range(9) if c != col): return False
    if any(board[r][col] == value for r in range(9) if r != row): return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    return not any(board[r][c] == value for r in range(br, br+3) for c in range(bc, bc+3) if (r,c)!=(row,col))

def sudoku_solved():
    return st.session_state.sudoku_board == SOLUTION

def top_progress():
    steps = ["Sudoku", "Memory", "Quiz", "Gift", "Cake", "Letter", "Love cards"]
    current = st.session_state.scene
    idx = {"sudoku":0,"memory":1,"quiz":2,"gift":3,"cake":4,"letter":5,"reasons":6}.get(current,0)
    st.caption("　".join(("🟠" if i == idx else "💗" if i < idx else "⚪") for i in range(len(steps))))
    st.caption(f"Level {idx+1} of {len(steps)} · {steps[idx]}")

def show_sudoku():
    st.markdown('<div class="heart-title">Easy Sudoku 💗</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">9×9 board · numbers 1–9</div>', unsafe_allow_html=True)
    st.write("Fill the heart-marked blanks with 1–9. No repeats in any row, column, or 3×3 box.")

    board = st.session_state.sudoku_board
    if not st.session_state.sudoku_started:
        if st.button("💗 Start Sudoku", use_container_width=True):
            st.session_state.sudoku_started = True
            st.rerun()
        if st.button("Continue", use_container_width=True):
            go("memory")
            st.rerun()
        # Show the puzzle preview before starting.
        html = ['<div class="sudoku-wrap"><table class="sudoku">']
        for r in range(9):
            html.append("<tr>")
            for c in range(9):
                val = board[r][c]
                bg = "#fff" if (r+c)%2 == 0 else "#faeef4"
                borders = [
                    "border-top:3px solid #3a1f3d" if r % 3 == 0 else "",
                    "border-left:3px solid #3a1f3d" if c % 3 == 0 else "",
                    "border-right:3px solid #3a1f3d" if c == 8 else "",
                    "border-bottom:3px solid #3a1f3d" if r == 8 else "",
                ]
                content = str(val) if val else "♡"
                color = INK if val else "#e99abb"
                html.append(f'<td style="background:{bg};color:{color};{";".join(x for x in borders if x)}">{content}</td>')
            html.append("</tr>")
        html.append("</table></div>")
        st.markdown("".join(html), unsafe_allow_html=True)
        return

    # Each heart-marked blank is an input directly inside the board.
    # Select a number in that cell; no separate row/column selector is needed.
    st.caption("Click a heart cell and choose its number directly in the grid.")
    cell_options = ["♡"] + [str(n) for n in range(1, 10)]
    changed_cells = []
    for r in range(9):
        cols = st.columns(9, gap="small")
        for c in range(9):
            with cols[c]:
                if (r, c) in HEART_BLANKS:
                    current = board[r][c]
                    current_label = str(current) if current else "♡"
                    choice = st.selectbox(
                        f"Row {r+1}, column {c+1}",
                        cell_options,
                        index=cell_options.index(current_label),
                        key=f"sudoku_cell_{r}_{c}",
                        label_visibility="collapsed",
                    )
                    if choice != current_label:
                        changed_cells.append((r, c, choice))
                else:
                    st.markdown(
                        f"<div style='height:39px;display:flex;align-items:center;justify-content:center;"
                        f"font-weight:700;color:{INK};background:{'#fff' if (r+c)%2 == 0 else '#faeef4'};"
                        f"border:1px solid #cda9bb;border-top:{'3px solid #3a1f3d' if r%3==0 else '1px solid #cda9bb'};"
                        f"border-left:{'3px solid #3a1f3d' if c%3==0 else '1px solid #cda9bb'};"
                        f"border-right:{'3px solid #3a1f3d' if c==8 else '1px solid #cda9bb'};"
                        f"border-bottom:{'3px solid #3a1f3d' if r==8 else '1px solid #cda9bb'};"
                        f"box-sizing:border-box'>{board[r][c]}</div>",
                        unsafe_allow_html=True,
                    )

    # Apply one changed cell per rerun and validate it.
    if changed_cells:
        r, c, choice = changed_cells[0]
        value = 0 if choice == "♡" else int(choice)
        if value == 0:
            board[r][c] = 0
            st.session_state.last_message = ""
        elif sudoku_valid(board, r, c, value):
            board[r][c] = value
            st.session_state.last_message = "Correct move! Keep going. 💗"
        else:
            st.session_state.last_message = "No repeats in that row, column, or 3×3 box."
        st.session_state.sudoku_board = board
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Reset puzzle", use_container_width=True):
            st.session_state.sudoku_board = [row[:] for row in PUZZLE]
            st.session_state.last_message = ""
            st.rerun()
    with c2:
        if st.button("Skip to Memory Match", use_container_width=True):
            go("memory")
            st.rerun()

    if st.session_state.last_message:
        if "No repeats" in st.session_state.last_message:
            st.warning(st.session_state.last_message)
        else:
            st.info(st.session_state.last_message)

    if sudoku_solved():
        st.success("Perfect! You solved the Sudoku! ❤️")
        if st.button("Continue to Memory Match", use_container_width=True):
            go("memory")
            st.rerun()

def show_memory():
    st.markdown('<div class="heart-title">Memory Match 💎</div>', unsafe_allow_html=True)
    st.write("Flip two cards and find all matching pairs.")
    if not st.session_state.memory_cards:
        go("memory"); st.rerun()
    cards = st.session_state.memory_cards
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            if i in st.session_state.memory_matched:
                label = f"{CONFIG['pairs'][cards[i]][0]}  {CONFIG['pairs'][cards[i]][2]}"
                st.success(label)
            elif i in st.session_state.memory_flipped:
                st.info(f"{CONFIG['pairs'][cards[i]][0]}  {CONFIG['pairs'][cards[i]][2]}")
            else:
                if st.button("💗 ?", key=f"memory_{i}", use_container_width=True):
                    if len(st.session_state.memory_flipped) < 2:
                        st.session_state.memory_flipped.append(i)
                        if len(st.session_state.memory_flipped) == 2:
                            a,b = st.session_state.memory_flipped
                            if cards[a] == cards[b]:
                                st.session_state.memory_matched.extend([a,b])
                                st.session_state.last_message = CONFIG["pairs"][cards[a]][1]
                                st.session_state.memory_flipped = []
                        st.rerun()
    # The columns above render in a single row; provide a second row for the remaining four cards.
    cols2 = st.columns(4)
    for j, col in enumerate(cols2, start=4):
        with col:
            if j in st.session_state.memory_matched:
                st.success(f"{CONFIG['pairs'][cards[j]][0]}  {CONFIG['pairs'][cards[j]][2]}")
            elif j in st.session_state.memory_flipped:
                st.info(f"{CONFIG['pairs'][cards[j]][0]}  {CONFIG['pairs'][cards[j]][2]}")
            else:
                if st.button("💗 ?", key=f"memory_{j}", use_container_width=True):
                    if len(st.session_state.memory_flipped) < 2:
                        st.session_state.memory_flipped.append(j)
                        if len(st.session_state.memory_flipped) == 2:
                            a,b = st.session_state.memory_flipped
                            if cards[a] == cards[b]:
                                st.session_state.memory_matched.extend([a,b])
                                st.session_state.last_message = CONFIG["pairs"][cards[a]][1]
                                st.session_state.memory_flipped = []
                        st.rerun()
    if st.session_state.last_message:
        st.info(st.session_state.last_message)
    if len(st.session_state.memory_flipped) == 2 and not (cards[st.session_state.memory_flipped[0]] == cards[st.session_state.memory_flipped[1]]):
        if st.button("Hide unmatched cards and try again", use_container_width=True):
            st.session_state.memory_flipped = []
            st.rerun()
    if len(st.session_state.memory_matched) == len(cards):
        st.success("All pairs matched!")
        if st.button("Continue to Quiz", use_container_width=True):
            go("quiz"); st.rerun()
    elif st.button("Continue to Quiz", use_container_width=True):
        go("quiz"); st.rerun()
    st.caption("If two cards do not match, click Reset cards to try again.")
    if st.button("Reset cards"):
        go("memory"); st.rerun()

def show_quiz():
    st.markdown('<div class="heart-title">Birthday Quiz 🎂</div>', unsafe_allow_html=True)
    i = st.session_state.quiz_i
    q, opts, correct = CONFIG["quiz"][i]
    st.write(f"Question {i+1} of {len(CONFIG['quiz'])}")
    choice = st.radio(q, opts, key=f"quiz_choice_{i}")
    if st.button("Check answer", use_container_width=True):
        idx = opts.index(choice)
        if idx == correct:
            st.success("Correct! 💗")
            if i + 1 < len(CONFIG["quiz"]):
                st.session_state.quiz_i += 1
                st.rerun()
            else:
                st.session_state.scene = "gift"
                st.rerun()
        else:
            st.error("Hmm, are you sure? Try again!")

def show_gift():
    st.markdown('<div class="heart-title">You did it! 🎁</div>', unsafe_allow_html=True)
    st.write("Click the box to open your gift.")
    if not st.session_state.gift_open:
        st.markdown("<div style='text-align:center;font-size:7rem'>🎁</div>", unsafe_allow_html=True)
        if st.button("Open your gift", use_container_width=True):
            st.session_state.gift_open = True; st.rerun()
    else:
        st.balloons()
        st.success("Surprise! A little birthday love just for you. 💗")
        if st.button("Continue to the cake", use_container_width=True):
            go("cake"); st.rerun()

def show_cake():
    st.markdown('<div class="heart-title">Happy Birthday, Martin! 🎂</div>', unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-size:7rem'>🎂🕯️🕯️🕯️</div>", unsafe_allow_html=True)
    st.write("There's a little gift waiting. Make a wish and blow out the candles!")
    if not st.session_state.candles_blown:
        if st.button("💨 Blow out the candles", use_container_width=True):
            st.session_state.candles_blown = True
            st.balloons()
            st.rerun()
    else:
        st.success("Make a wish! ✨")
        if st.button("Read your birthday letter", use_container_width=True):
            go("letter"); st.rerun()

def show_letter():
    st.markdown(f'<div class="heart-title">Happy Birthday, {CONFIG["name"]}! 💌</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#fff;padding:1.5rem;border-radius:18px;white-space:pre-wrap;line-height:1.8;color:{INK}">{CONFIG["letter"]}</div>', unsafe_allow_html=True)
    photo_path = Path(__file__).parent / CONFIG["photo"]
    if photo_path.exists():
        st.image(str(photo_path), caption=CONFIG["caption"], use_container_width=True)
    else:
        st.caption(f"Add your photo as `{CONFIG['photo']}` in the same folder to show it here.")
    if st.button("Open the love cards 💗", use_container_width=True):
        go("reasons"); st.rerun()

def show_reasons():
    st.markdown('<div class="heart-title">Reasons I Love You 💗</div>', unsafe_allow_html=True)
    st.write("Tap a card to reveal it.")
    cols = st.columns(2)
    for i, reason in enumerate(CONFIG["reasons"]):
        with cols[i % 2]:
            if i in st.session_state.opened_reasons:
                st.success(reason)
            elif st.button(f"💗 Tap to open #{i+1}", key=f"reason_{i}", use_container_width=True):
                st.session_state.opened_reasons.add(i); st.rerun()
    st.markdown("<div style='text-align:center;color:#7a5a7c'>Made with love 💕</div>", unsafe_allow_html=True)
    if st.button("Play again", use_container_width=True):
        go("sudoku"); st.rerun()

init_state()
st.markdown(f'<div class="heart-title">Happy Birthday, {CONFIG["name"]} 💗</div>', unsafe_allow_html=True)
top_progress()

SCENES = {
    "sudoku": show_sudoku,
    "memory": show_memory,
    "quiz": show_quiz,
    "gift": show_gift,
    "cake": show_cake,
    "letter": show_letter,
    "reasons": show_reasons,
}
SCENES[st.session_state.scene]()
