# Birthday Quest 💗 — Streamlit version

This is a browser/mobile-friendly conversion of the original Pygame Birthday Quest. It keeps the original game sequence, quiz, heart Sudoku, memory cards, gift, birthday cake, letter, photo, and reasons cards. The Pygame drawing loop was replaced with Streamlit controls because Pygame desktop windows do not render inside a Streamlit Cloud web page.

## Files
- `HBD.py` — web app entry point
- `us.png` — photo used in the birthday letter
- `requirements.txt` — dependencies for Streamlit Community Cloud

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run HBD.py
```

## Publish as a link
1. Create a GitHub repository and upload `HBD.py`, `us.png`, and `requirements.txt` to the repository root.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select the repository and branch, set **Main file path** to `HBD.py`, then deploy.
4. Open the resulting public app URL on an iPhone or Android phone.

No `pygame` dependency is needed for this browser version.
