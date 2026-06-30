from tkinter import *
from tkinter import messagebox
import json
import pyttsx3
import threading
import numpy as np
from difflib import get_close_matches
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
import pickle

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)





# ─── Engine & Model Setup ─────────────────────────────────────────────────────
engine = pyttsx3.init()

# !! PASTE YOUR FREE GROQ KEY HERE (from groq.com — no card needed) !!


# Load sentence transformer model once at startup
print("[1/3] Loading AI embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ─── Load Dictionary Data ─────────────────────────────────────────────────────
# data.json should be in the SAME FOLDER as this script
import pathlib
DATA_PATH = pathlib.Path(__file__).parent / "data.json"

print("[2/3] Loading dictionary...")
data = json.load(open(DATA_PATH))

# Pre-compute embeddings for ALL meanings
# print("[3/3] Building semantic index (first run takes ~30s)...")
# all_words = list(data.keys())
# all_meanings_text = [word + ": " + " ".join(data[word]) for word in all_words]
# meaning_embeddings = embedding_model.encode(all_meanings_text, show_progress_bar=True)



import pickle

EMBEDDINGS_FILE = "meaning_embeddings.npy"
WORDS_FILE = "all_words.pkl"

import pickle

CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

EMBEDDINGS_FILE = os.path.join(CACHE_DIR, "meaning_embeddings.npy")
WORDS_FILE = os.path.join(CACHE_DIR, "all_words.pkl")

all_words = list(data.keys())

if os.path.exists(EMBEDDINGS_FILE):

    print("[3/3] Loading cached semantic index...")

    meaning_embeddings = np.load(EMBEDDINGS_FILE)

    with open(WORDS_FILE, "rb") as f:
        all_words = pickle.load(f)

else:

    print("[3/3] Building semantic index (first run only)...")

    all_meanings_text = [
        word + ": " + " ".join(data[word])
        for word in all_words
    ]

    meaning_embeddings = embedding_model.encode(
        all_meanings_text,
        show_progress_bar=True
    )

    np.save(EMBEDDINGS_FILE, meaning_embeddings)

    with open(WORDS_FILE, "wb") as f:
        pickle.dump(all_words, f)

    print("Semantic index saved successfully!")

print("Ready!\n")








# all_words = list(data.keys())

# if os.path.exists(EMBEDDINGS_FILE) and os.path.exists(WORDS_FILE):
#     print("[3/3] Loading semantic index...")
#     meaning_embeddings = np.load(EMBEDDINGS_FILE)
#     with open(WORDS_FILE, "rb") as f:
#         all_words = pickle.load(f)

# else:
#     print("[3/3] Building semantic index (only first run)...")

#     all_meanings_text = [
#         word + ": " + " ".join(data[word])
#         for word in all_words
#     ]

#     meaning_embeddings = embedding_model.encode(
#         all_meanings_text,
#         show_progress_bar=True
#     )

#     np.save(EMBEDDINGS_FILE, meaning_embeddings)

#     with open(WORDS_FILE, "wb") as f:
#         pickle.dump(all_words, f)

#     print("Semantic index saved.")



# print("Ready! All features unlocked.\n")

# ─── Audio ────────────────────────────────────────────────────────────────────
def wordaudio():
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(enterwordentry.get())
    engine.runAndWait()

def meaningaudio():
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 150)
    engine.say(textarea.get(1.0, END))
    engine.runAndWait()

# ─── Helpers ──────────────────────────────────────────────────────────────────
def iexit():
    if messagebox.askyesno('Confirm', 'Do you want to exit?'):
        root.destroy()

def clear():
    enterwordentry.delete(0, END)
    textarea.config(state=NORMAL)
    textarea.delete(1.0, END)
    textarea.config(state=DISABLED)
    llm_text.config(state=NORMAL)
    llm_text.delete(1.0, END)
    llm_text.config(state=DISABLED)
    set_status("")

def show_meaning(word, meaning):
    textarea.config(state=NORMAL)
    textarea.delete(1.0, END)
    for item in meaning:
        textarea.insert(END, u'\u2022 ' + item + '\n\n')
    textarea.config(state=DISABLED)

def set_status(msg, color="#7ec8e3"):
    status_label.config(text=msg, fg=color)
    root.update_idletasks()

# ─── FEATURE 1: Classic + Semantic Search ─────────────────────────────────────
def search():
    word = enterwordentry.get().strip().lower()
    if not word:
        return

    # Exact match
    if word in data:
        show_meaning(word, data[word])
        set_status(f"✓ Exact match found: '{word}'", "#50fa7b")
        llm_generate_example(word, data[word])
        return

    # Fuzzy match
    close = get_close_matches(word, data.keys())
    if close:
        if messagebox.askyesno('Did you mean...', f'Did you mean "{close[0]}"?'):
            show_meaning(close[0], data[close[0]])
            set_status(f"✓ Fuzzy match: '{close[0]}'", "#50fa7b")
            llm_generate_example(close[0], data[close[0]])
        else:
            messagebox.showinfo('Info', 'Please type a correct word')
            enterwordentry.delete(0, END)
        return

    # Semantic fallback
    set_status("No exact match — searching by meaning...", "#f5a623")
    query_vec = embedding_model.encode([word])
    scores = np.dot(meaning_embeddings, query_vec.T).flatten()
    top_idx = int(np.argmax(scores))
    top_word = all_words[top_idx]
    score = float(scores[top_idx])

    if score > 0.4:
        if messagebox.askyesno('Semantic Match',
            f'No exact match for "{word}".\n\nClosest semantic match: "{top_word}"\nSimilarity score: {score:.2f}\n\nShow its meaning?'):
            show_meaning(top_word, data[top_word])
            set_status(f"✓ Semantic match: '{top_word}' (score {score:.2f})", "#a78bfa")
            llm_generate_example(top_word, data[top_word])
    else:
        messagebox.showerror('Not Found', f'Could not find "{word}" or anything semantically close.')
        enterwordentry.delete(0, END)
        set_status("No match found.", "#e94560")

# ─── FEATURE 2: Reverse Dictionary ───────────────────────────────────────────
def reverse_search():
    phrase = reverse_entry.get().strip()
    if not phrase or phrase.startswith('e.g.'):
        messagebox.showinfo("Info", "Type a concept or description in the box above first.")
        return

    set_status("Searching by concept...", "#f5a623")
    root.update_idletasks()

    query_vec = embedding_model.encode([phrase])
    scores = np.dot(meaning_embeddings, query_vec.T).flatten()
    top_indices = np.argsort(scores)[::-1][:5]
    results = [(all_words[i], float(scores[i])) for i in top_indices]

    win = Toplevel(root)
    win.title("Reverse Dictionary Results")
    win.geometry("520x420+200+150")
    win.configure(bg='#1a1a2e')

    Label(win, text=f'Top matches for:', font=('arial', 10), bg='#1a1a2e', fg='#a0a0c0').pack(pady=(12,0))
    Label(win, text=f'"{phrase}"', font=('arial', 12, 'bold'), bg='#1a1a2e', fg='#f5a623').pack()

    for rank, (word, score) in enumerate(results, 1):
        frame = Frame(win, bg='#16213e', pady=6, padx=10)
        frame.pack(fill=X, padx=16, pady=5)

        Label(frame, text=f"#{rank}  {word.upper()}   score: {score:.3f}",
              font=('courier', 11, 'bold'), bg='#16213e', fg='white').pack(anchor=W)

        preview = data[word][0][:90] + "..." if len(data[word][0]) > 90 else data[word][0]
        Label(frame, text=preview, font=('arial', 9), bg='#16213e',
              fg='#a0a0c0', wraplength=460, justify=LEFT).pack(anchor=W, pady=(2,4))

        def use_word(w=word):
            win.destroy()
            enterwordentry.delete(0, END)
            enterwordentry.insert(0, w)
            search()

        Button(frame, text="Use this word →", font=('arial', 9, 'bold'),
               command=use_word, bg='#f5a623', fg='#1a1a2e',
               relief=FLAT, cursor='hand2', padx=10, pady=3).pack(anchor=E)

    set_status(f"Found top 5 semantic matches for your concept", "#50fa7b")

# ─── FEATURE 3: LLM Example Generation via GROQ (FREE) ───────────────────────
def llm_generate_example(word, meanings):
    def _generate():
        llm_text.config(state=NORMAL)
        llm_text.delete(1.0, END)
        llm_text.insert(END, "⏳ Generating AI examples via Groq (free)...\n")
        llm_text.config(state=DISABLED)
        set_status("Calling Groq API...", "#f5a623")

        try:
            meaning_str = meanings[0] if meanings else "unknown"
            prompt = f"""Word: "{word}"
Meaning: {meaning_str}

Write exactly 3 vivid example sentences using the word "{word}".
Each sentence must come from a different context (work, emotion, everyday life).
Make them memorable and clearly show the meaning.

Format:
1. [sentence]
2. [sentence]
3. [sentence]

Only output the 3 numbered sentences. Nothing else."""

            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",   # Free model on Groq
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            llm_text.config(state=NORMAL)
            llm_text.delete(1.0, END)
            llm_text.insert(END, f"AI examples for  '{word}' :\n\n{result}")
            llm_text.config(state=DISABLED)
            set_status(f"✓ AI examples ready for '{word}'", "#50fa7b")

        except Exception as e:
            llm_text.config(state=NORMAL)
            llm_text.delete(1.0, END)
            llm_text.insert(END, f"Groq API Error:\n{str(e)}\n\nGet your FREE key at groq.com\nThen paste it in line 13 of this file.")
            llm_text.config(state=DISABLED)
            set_status("API error — check your Groq key", "#e94560")

    threading.Thread(target=_generate, daemon=True).start()

# ─── UI ───────────────────────────────────────────────────────────────────────
root = Tk()
root.geometry('1100x760+50+30')
root.title('AI-Powered English Dictionary')
root.resizable(0, 0)
root.configure(bg='#1a1a2e')

# Header
header = Frame(root, bg='#16213e', pady=10)
header.pack(fill=X)
Label(header, text='AI-POWERED', font=('courier', 10, 'bold'), bg='#16213e', fg='#e94560').pack()
Label(header, text='ENGLISH DICTIONARY', font=('castellar', 20, 'bold'), bg='#16213e', fg='white').pack()
Label(header, text='Semantic Search  •  Reverse Lookup  •  AI Examples (Groq — Free)',
      font=('arial', 9), bg='#16213e', fg='#a0a0c0').pack(pady=(2,0))

# Status
status_label = Label(root, text="", font=('arial', 9, 'italic'), bg='#1a1a2e', fg='#7ec8e3')
status_label.pack(pady=(4, 0))

# Main frame
main = Frame(root, bg='#1a1a2e')
main.pack(fill=BOTH, expand=True, padx=20, pady=10)

# ── LEFT: Word Search ──
left = Frame(main, bg='#16213e', padx=15, pady=15)
left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,10))

Label(left, text='WORD SEARCH', font=('courier', 11, 'bold'), bg='#16213e', fg='#e94560').pack(anchor=W)
Label(left, text='Exact  ·  Fuzzy  ·  Semantic fallback', font=('arial', 8), bg='#16213e', fg='#606080').pack(anchor=W)
Frame(left, bg='#e94560', height=2).pack(fill=X, pady=6)

enterwordentry = Entry(left, font=('arial', 15, 'bold'), bd=0, relief=FLAT,
                        bg='#0f3460', fg='white', insertbackground='white', justify=CENTER)
enterwordentry.pack(fill=X, ipady=8, pady=4)
enterwordentry.focus_set()
enterwordentry.bind('<Return>', lambda e: search())

bf = Frame(left, bg='#16213e')
bf.pack(fill=X, pady=4)
Button(bf, text='🔍  SEARCH', font=('arial', 11, 'bold'), command=search,
       bg='#e94560', fg='white', relief=FLAT, cursor='hand2', padx=12, pady=6).pack(side=LEFT, padx=(0,6))
Button(bf, text='🔊 Word', font=('arial', 10), command=wordaudio,
       bg='#0f3460', fg='white', relief=FLAT, cursor='hand2', padx=8, pady=6).pack(side=LEFT, padx=(0,6))
Button(bf, text='🗑 Clear', font=('arial', 10), command=clear,
       bg='#333355', fg='white', relief=FLAT, cursor='hand2', padx=8, pady=6).pack(side=LEFT)

Label(left, text='DEFINITION', font=('courier', 10, 'bold'), bg='#16213e', fg='#7ec8e3').pack(anchor=W, pady=(12,2))
textarea = Text(left, font=('arial', 11), height=9, bd=0, relief=FLAT,
                wrap='word', bg='#0f3460', fg='white', padx=8, pady=8)
textarea.pack(fill=BOTH, expand=True)
textarea.config(state=DISABLED)

Button(left, text='🔊  Read Meaning Aloud', font=('arial', 10), command=meaningaudio,
       bg='#0f3460', fg='white', relief=FLAT, cursor='hand2', pady=6).pack(fill=X, pady=(8,0))

# ── RIGHT: Reverse + LLM ──
right = Frame(main, bg='#16213e', padx=15, pady=15)
right.pack(side=LEFT, fill=BOTH, expand=True)

Label(right, text='REVERSE DICTIONARY', font=('courier', 11, 'bold'), bg='#16213e', fg='#f5a623').pack(anchor=W)
Label(right, text='Describe a feeling or concept  →  find the word', font=('arial', 8), bg='#16213e', fg='#606080').pack(anchor=W)
Frame(right, bg='#f5a623', height=2).pack(fill=X, pady=6)

reverse_entry = Entry(right, font=('arial', 11), bd=0, relief=FLAT,
                       bg='#0f3460', fg='gray60', insertbackground='white')
placeholder = 'e.g. "nostalgia for a time you never lived"'
reverse_entry.insert(0, placeholder)

def on_focus_in(e):
    if reverse_entry.get() == placeholder:
        reverse_entry.delete(0, END)
        reverse_entry.config(fg='white')

def on_focus_out(e):
    if not reverse_entry.get():
        reverse_entry.insert(0, placeholder)
        reverse_entry.config(fg='gray60')

reverse_entry.bind('<FocusIn>', on_focus_in)
reverse_entry.bind('<FocusOut>', on_focus_out)
reverse_entry.bind('<Return>', lambda e: reverse_search())
reverse_entry.pack(fill=X, ipady=7, pady=(0,4))

Button(right, text='🧠  FIND WORD FROM CONCEPT', font=('arial', 11, 'bold'),
       command=reverse_search, bg='#f5a623', fg='#1a1a2e',
       relief=FLAT, cursor='hand2', pady=6).pack(fill=X, pady=(0,14))

Label(right, text='AI EXAMPLE SENTENCES', font=('courier', 11, 'bold'), bg='#16213e', fg='#50fa7b').pack(anchor=W)
Label(right, text='Groq (free)  ·  llama3-8b  ·  auto-generates on every search', font=('arial', 8), bg='#16213e', fg='#606080').pack(anchor=W)
Frame(right, bg='#50fa7b', height=2).pack(fill=X, pady=6)

llm_text = Text(right, font=('arial', 11), height=13, bd=0, relief=FLAT,
                wrap='word', bg='#0a2a1a', fg='#50fa7b', padx=8, pady=8)
llm_text.pack(fill=BOTH, expand=True)
llm_text.config(state=DISABLED)

# Footer
footer = Frame(root, bg='#16213e', pady=8)
footer.pack(fill=X, side=BOTTOM)
Button(footer, text='✕  EXIT', font=('arial', 10, 'bold'), command=iexit,
       bg='#e94560', fg='white', relief=FLAT, cursor='hand2', padx=20, pady=5).pack()

root.mainloop()
