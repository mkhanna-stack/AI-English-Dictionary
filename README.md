AI-Powered English Dictionary

*LexiSense AI– AI English Dictionary*

Semantic Search • Reverse Dictionary • AI-Generated Contextual Examples

A desktop AI-powered English Dictionary built with Python, Sentence Transformers, and Groq LLM.

Unlike a traditional dictionary, this application understands semantic meaning rather than relying only on exact keyword matches.

Features:


*Exact Search*

Search any English word instantly.




*Fuzzy Search*

Automatically detects spelling mistakes.



Example:

hapy

↓

happy
Semantic Search

Understands meaning using sentence embeddings.



Example:

can't sleep

↓

insomnia

instead of returning "Word not found."

Reverse Dictionary

Describe a concept.




Example

nostalgia for a place you've never visited

↓

Returns the closest matching English words.

AI Generated Example Sentences

Uses the Groq API to generate

contextual
natural
memorable

example sentences using the searched word.




*Text-to-Speech*

Read

words

and

meanings

aloud.




*Cached Semantic Embeddings*

Embeddings are generated only once.

First startup:

~5–10 minutes

Subsequent launches:

2–5 seconds

using cached embeddings.



*Tech Stack*
Python
Tkinter
Sentence Transformers
MiniLM-L6-v2
NumPy
Groq API
pyttsx3




*Project Architecture*

User

↓

Search Query

↓

Exact Search

↓

Fuzzy Search

↓

Semantic Search

↓

Sentence Transformer

↓

Embedding Similarity

↓

Definition

↓

Groq LLM

↓

AI Generated Examples




*Installation*

Clone the repository

git clone https://github.com/yourusername/AI-English-Dictionary.git

Create virtual environment

python -m venv venv

Activate

Windows

venv\Scripts\activate

Install

pip install -r requirements.txt

Create

.env
GROQ_API_KEY=YOUR_KEY

Run

python smart_dictionary.py
First Run

The first launch generates semantic embeddings for the dictionary.

This may take several minutes depending on the hardware.

All subsequent launches automatically load the cached embeddings for much faster startup.





*Future Improvements*

FAISS vector search
Word of the Day
Search history
Multi-language support
Streamlit/Web interface
Voice-based semantic search





*Screenshots*

Home

![alt text](interface-1.png)

Semantic Search

![alt text](Semnatic-search.png)

Reverse Dictionary

![alt text](<reverse dict.png>)

AI Generated Examples
![alt text](<dictionary search.png>)

fuzzy search
![alt text](<fuzzy search.png>)



*Project Structure*

AI-English-Dictionary/

│

├── smart_dictionary.py

├── data.json

├── requirements.txt

├── README.md

├── .gitignore

├── .env.example

│

├── assets/

│      home.png

│      semantic-search.png

│      reverse-search.png

│      ai-example.png

│

└── cache/

       (generated automatically)