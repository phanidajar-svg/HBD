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
.block-container {{ max-width: 560px; padding: 1.1rem 1rem 2.2rem; }}
h1, h2, h3, p, label {{ color: {INK} !important; }}
div.stButton > button {{
  border-radius: 18px; border: 1px solid #f5b7cc; background: #ff4f78;
  color: white; font-weight: 650; min-height: 2.7rem;
}}
div.stButton > button:hover {{ background: #e63e68; color: white; border-color: #e63e68; }}
div[data-testid="stRadio"] label {{ color: {INK} !important; }}
/* Sudoku-specific responsive CSS is defined below and scoped to its board. */
.heart-title {{ text-align:center; color:{ACC}; font-size: clamp(1.55rem, 5vw, 2.25rem); font-weight:850; line-height:1.2; margin: .35rem 0 .65rem; }}
.subtitle {{ text-align:center; color:{SOFT}; font-size:1rem; margin-bottom:.7rem; }}
.sudoku-card {{ background:rgba(255,255,255,.65); border:1px solid #f4c5d5; border-radius:20px; padding:clamp(8px, 2.5vw, 15px); box-shadow:0 8px 24px rgba(125,55,88,.08); margin:.7rem 0 1rem; }}
.sudoku-wrap {{ width:100%; max-width:440px; margin:0 auto; }}
.sudoku {{ border-collapse:collapse; table-layout:fixed; width:100%; aspect-ratio:1/1; }}
.sudoku td {{ width:11.111%; height:auto; aspect-ratio:1/1; text-align:center; vertical-align:middle; border:1px solid #e5b7ca; font-size:clamp(12px, 3.8vw, 19px); font-weight:750; padding:0; }}
.sudoku td.fixed {{ background:#fffafd; color:{INK}; }}
.sudoku td.blank {{ background:#fff0f6; color:#e56b9b; }}
.sudoku td.filled {{ background:#ffe0eb; color:{ACC}; }}
.sudoku td.selected {{ outline:2px solid {ACC}; outline-offset:-3px; background:#ffd0e0; }}
@media (max-width:480px) {{ .block-container {{ padding-left:.35rem; padding-right:.35rem; }} .stButton button {{ font-size:.88rem; }} }}
/* Direct-tap Sudoku board: keep nine square cells in each row on phones. */
div.st-key-sudoku_grid div[data-testid="stHorizontalBlock"] {{
  flex-wrap: nowrap !important; gap: 1px !important;
}}
div.st-key-sudoku_grid div[data-testid="column"] {{
  min-width: 0 !important; width: 0 !important; flex: 1 1 0% !important;
  padding: 0 !important;
}}
div.st-key-sudoku_grid div.stButton > button {{
  width: 100% !important; min-width: 0 !important; aspect-ratio: 1 / 1 !important;
  height: auto !important; padding: 0 !important; margin: 0 !important;
  border-radius: 0 !important; font-size: clamp(10px, 3vw, 16px) !important;
  line-height: 1 !important; white-space: nowrap !important;
}}
div.st-key-sudoku_grid div.stButton > button:disabled {{
  opacity: 1 !important; background: #fffafd !important; color: #3a1f3d !important;
  border: 1px solid #e5b7ca !important;
}}
@media (max-width:480px) {{ .block-container {{ padding-left:.65rem; padding-right:.65rem; }} .stButton button {{ font-size:.88rem; }} }}
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
    st.markdown('<div class="subtitle">A little puzzle, made with love · 9×9</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#7a5a7c;font-size:.94rem;margin-bottom:.7rem">'
        'Tap a heart cell on the board, then tap a number below. No repeats in any row, column, or 3×3 box.'
        '</div>', unsafe_allow_html=True
    )
    board = st.session_state.sudoku_board

    if not st.session_state.sudoku_started:
        html = ['<div class="sudoku-card"><div class="sudoku-wrap"><table class="sudoku">']
        for r in range(9):
            html.append("<tr>")
            for c in range(9):
                val = board[r][c]
                cls = "fixed" if val else "blank"
                borders = [
                    "border-top:3px solid #6b3556" if r % 3 == 0 else "",
                    "border-left:3px solid #6b3556" if c % 3 == 0 else "",
                    "border-right:3px solid #6b3556" if c == 8 else "",
                    "border-bottom:3px solid #6b3556" if r == 8 else "",
                ]
                content = str(val) if val else "♡"
                html.append(f'<td class="{cls}" style="{";".join(x for x in borders if x)}">{content}</td>')
            html.append("</tr>")
        html.append("</table></div></div>")
        st.markdown("".join(html), unsafe_allow_html=True)
        if st.button("💗 Start Sudoku", use_container_width=True):
            st.session_state.sudoku_started = True
            st.rerun()
        if st.button("Skip to Memory Match →", use_container_width=True):
            go("memory")
            st.rerun()
        return

    # Tap a heart cell directly; no row/column dropdown is needed.
    selected = st.session_state.sudoku_selected
    with st.container(key="sudoku_grid"):
        for r in range(9):
            cols = st.columns(9, gap=None)
            for c, col in enumerate(cols):
                with col:
                    val = board[r][c]
                    editable = (r, c) in HEART_BLANKS
                    is_selected = selected == (r, c)
                    if editable:
                        label = str(val) if val else "♡"
                        if st.button(
                            label,
                            key=f"sudoku_cell_{r}_{c}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary",
                        ):
                            st.session_state.sudoku_selected = (r, c)
                            st.rerun()
                    else:
                        st.button(
                            str(val), key=f"sudoku_fixed_{r}_{c}",
                            use_container_width=True, disabled=True,
                        )

    selected = st.session_state.sudoku_selected
    if selected is None:
        st.info("Tap a ♡ cell to choose where to put a number.")
    else:
        r, c = selected
        st.markdown(
            f'<div style="text-align:center;color:#7a5a7c;margin:10px 0">'
            f'💗 Selected: Row {r + 1} · Column {c + 1} · Current: {board[r][c] or "♡"}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="text-align:center;color:#7a5a7c;font-weight:700;margin:.35rem 0">Choose a number</div>', unsafe_allow_html=True)
        for row_nums in ((1, 2, 3), (4, 5, 6), (7, 8, 9)):
            cols = st.columns(3, gap="small")
            for col, num in zip(cols, row_nums):
                with col:
                    if st.button(str(num), key=f"sudoku_num_{num}", use_container_width=True):
                        board[r][c] = num
                        st.session_state.sudoku_board = board
                        st.session_state.last_message = (
                            "There is a repeat in this row, column, or 3×3 box. Try another number."
                            if not sudoku_valid(board, r, c, num)
                            else "Nice move! Keep going. 💗"
                        )
                        st.rerun()
        if st.button("⌫ Clear selected cell", use_container_width=True):
            board[r][c] = 0
            st.session_state.sudoku_board = board
            st.session_state.last_message = ""
            st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Reset puzzle", use_container_width=True):
            st.session_state.sudoku_board = [row[:] for row in PUZZLE]
            st.session_state.sudoku_selected = None
            st.session_state.last_message = ""
            st.rerun()
    with c2:
        if st.button("Skip to Memory →", use_container_width=True):
            go("memory")
            st.rerun()

    if st.session_state.last_message:
        if "repeat" in st.session_state.last_message:
            st.warning(st.session_state.last_message)
        else:
            st.info(st.session_state.last_message)
    if sudoku_solved():
        st.success("Perfect! You solved the Sudoku! ❤️")
        if st.button("Continue to Memory Match 💎", use_container_width=True):
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

def birthday_music_player():
    """Happy Birthday instrumental with browser-native play/pause and volume controls."""
    music_path = Path(__file__).parent / "cute_instrumental.wav"
    st.markdown(
        '<div style="text-align:center;color:#7a5a7c;font-weight:650;">🎵 A little birthday music for you 💗</div>',
        unsafe_allow_html=True,
    )
    if music_path.exists():
        # Browsers on phones usually require a user tap before audio can start.
        # Native audio controls provide play/pause and volume controls on mobile.
        st.audio(str(music_path), format="audio/wav", loop=True, autoplay=False)
        st.caption("Tap ▶ to play. You can pause or adjust the volume anytime.")
    else:
        st.info("Add `cute_instrumental.wav` beside `HBD.py` to enable the birthday music.")


def show_cake():
    st.markdown('<div class="heart-title">Happy Birthday, Martin! 🎂</div>', unsafe_allow_html=True)
    birthday_music_player()
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
    birthday_music_player()
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
