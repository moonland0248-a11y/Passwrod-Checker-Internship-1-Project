#!/usr/bin/env python3
"""
Password Strength & Breach Checker - Advanced GUI
Features: Strength Meter, Show/Hide, Password Generator
"""

import re             #pattern making
import hashlib        #creates hash
import requests       #talks to the internet
import random         #creats random passwords
import string         #readymade letters ,nos ,symbols
import tkinter as tk  #main gui library
from tkinter import ttk, messagebox, scrolledtext  #popup windows  /  scrollable window
from datetime import datetime    # show date n time

# ---------------- Colors ----------------
BG_COLOR = "#0f172a"
CARD_COLOR = "#1e293b"
ACCENT = "#38bdf8"
TEXT_COLOR = "#e2e8f0"
WEAK = "#ef4444"
MEDIUM = "#f59e0b"
STRONG = "#22c55e"
VERY_STRONG = "#4ade80"
ENTRY_BG = "#334155"

COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password1",
    "111111", "12345678", "admin", "welcome", "monkey",
    "login", "letmein", "123123", "football", "princess"
}

def check_strength(password: str) -> dict:
    score = 0
    feedback = []

    length = len(password)
    if length >= 12:
        score += 2
    elif length >= 8:
        score += 1
    else:
        feedback.append("Password is too short (minimum 8 characters)")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add special characters (!@#$%^&*)")

    if password.lower() in COMMON_PASSWORDS:
        score = 0
        feedback.append("This is a very common password — highly insecure")

    if re.search(r"(.)\1{2,}", password):
        score = max(0, score - 1)
        feedback.append("Avoid repeated characters")

    if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde)", password.lower()):
        score = max(0, score - 1)
        feedback.append("Avoid sequential characters")

# ------ Rating --------

    if score >= 6:
        rating = "Very Strong"
    elif score >= 4:
        rating = "Strong"
    elif score >= 2:
        rating = "Medium"
    else:
        rating = "Weak"

    return {"score": score, "rating": rating, "feedback": feedback, "length": length}

# ------ Checking Comprimized passwords -------

def check_pwned(password: str) -> int:
    try:
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return -1
        hashes = (line.split(":") for line in res.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return int(count)
        return 0
    except Exception:
        return -1

def generate_password():
    length = int(length_var.get())
    chars = string.ascii_letters + string.digits
    if symbols_var.get():
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    entry.delete(0, tk.END)
    entry.insert(0, password)
    if show_var.get():
        entry.config(show="")
    else:
        entry.config(show="•")
    analyze_password()

def toggle_password():
    if show_var.get():
        entry.config(show="")
    else:
        entry.config(show="•")

def analyze_password():
    password = entry.get()
    if not password:
        messagebox.showwarning("Warning", "Please enter a password")
        return

    strength = check_strength(password)
    pwned = check_pwned(password)

    # Update Rating + Color
    rating = strength["rating"]
    if rating == "Very Strong":
        color = VERY_STRONG
        progress["value"] = 100
    elif rating == "Strong":
        color = STRONG
        progress["value"] = 75
    elif rating == "Medium":
        color = MEDIUM
        progress["value"] = 45
    else:
        color = WEAK
        progress["value"] = 20

    rating_label.config(text=rating, foreground=color)
    score_label.config(text=f"Score: {strength['score']}/6")
    style.configure("Custom.Horizontal.TProgressbar", background=color)

    # Report
    report = f"Password Length : {strength['length']} characters\n"
    report += "────────────────────────────────────────\n\n"

    if strength["feedback"]:
        report += "Suggestions to improve:\n"
        for tip in strength["feedback"]:
            report += f"  •  {tip}\n"
    else:
        report += "✓  No major structural weaknesses found\n"

    report += "\n────────────────────────────────────────\n"

    if pwned == -1:
        report += "Breach Status  :  Could not reach Have I Been Pwned\n"
    elif pwned == 0:
        report += "Breach Status  :  Not found in known data breaches ✓\n"
    else:
        report += f"Breach Status  :  FOUND in {pwned:,} breaches! ⚠\n"
        report += "                 → Change this password immediately\n"

    result_box.config(state="normal")
    result_box.delete(1.0, tk.END)
    result_box.insert(tk.END, report)
    result_box.config(state="disabled")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Password Strength & Breach Checker")
root.geometry("600x700")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.Horizontal.TProgressbar", troughcolor="#334155", background=ACCENT, thickness=12)

main_frame = tk.Frame(root, bg=CARD_COLOR, padx=25, pady=20)
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# Title
tk.Label(main_frame, text="Password Strength Checker", font=("Segoe UI", 18, "bold"),
         bg=CARD_COLOR, fg=ACCENT).pack(pady=(0, 3))
tk.Label(main_frame, text="Strength • Breach Check • Generator", font=("Segoe UI", 9),
         bg=CARD_COLOR, fg="#94a3b8").pack(pady=(0, 15))

# Password Entry + Show/Hide
tk.Label(main_frame, text="Enter Password", font=("Segoe UI", 10),
         bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")

entry_frame = tk.Frame(main_frame, bg=CARD_COLOR)
entry_frame.pack(fill="x", pady=(5, 8))

entry = tk.Entry(entry_frame, font=("Segoe UI", 12), bg=ENTRY_BG, fg="white",
                 insertbackground="white", relief="flat", show="•")
entry.pack(side="left", fill="x", expand=True, ipady=7)
entry.focus()

show_var = tk.BooleanVar()
show_btn = tk.Checkbutton(entry_frame, text="Show", variable=show_var, command=toggle_password,
                          bg=CARD_COLOR, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
                          activebackground=CARD_COLOR, activeforeground=ACCENT)
show_btn.pack(side="right", padx=(8, 0))

# Progress Bar
progress = ttk.Progressbar(main_frame, style="Custom.Horizontal.TProgressbar",
                           orient="horizontal", length=400, mode="determinate")
progress.pack(pady=(5, 5))

# Rating
rating_label = tk.Label(main_frame, text="—", font=("Segoe UI", 20, "bold"),
                        bg=CARD_COLOR, fg=TEXT_COLOR)
rating_label.pack()
score_label = tk.Label(main_frame, text="Score: - /6", font=("Segoe UI", 10),
                       bg=CARD_COLOR, fg="#94a3b8")
score_label.pack(pady=(0, 12))

# Buttons
btn_frame = tk.Frame(main_frame, bg=CARD_COLOR)
btn_frame.pack(pady=(0, 15))

tk.Button(btn_frame, text="Analyze Password", font=("Segoe UI", 10, "bold"),
          bg=ACCENT, fg="#0f172a", relief="flat", cursor="hand2",
          command=analyze_password, padx=15, pady=6).pack(side="left", padx=5)

# -------- Password Generator Section --------
gen_frame = tk.LabelFrame(main_frame, text=" Password Generator ", font=("Segoe UI", 9, "bold"),
                          bg=CARD_COLOR, fg=ACCENT, padx=10, pady=8)
gen_frame.pack(fill="x", pady=(5, 15))

gen_options = tk.Frame(gen_frame, bg=CARD_COLOR)
gen_options.pack()

tk.Label(gen_options, text="Length:", bg=CARD_COLOR, fg=TEXT_COLOR).pack(side="left")
length_var = tk.StringVar(value="16")
length_spin = ttk.Spinbox(gen_options, from_=8, to=64, textvariable=length_var, width=5)
length_spin.pack(side="left", padx=8)

symbols_var = tk.BooleanVar(value=True)
tk.Checkbutton(gen_options, text="Include Symbols", variable=symbols_var,
               bg=CARD_COLOR, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
               activebackground=CARD_COLOR).pack(side="left", padx=8)

tk.Button(gen_frame, text="Generate Strong Password", font=("Segoe UI", 9, "bold"),
          bg="#22c55e", fg="white", relief="flat", cursor="hand2",
          command=generate_password, padx=10, pady=4).pack(pady=(8, 0))

# Result Box
result_box = scrolledtext.ScrolledText(main_frame, width=55, height=10,
                                       font=("Consolas", 10), bg="#0f172a",
                                       fg=TEXT_COLOR, relief="flat", state="disabled")
result_box.pack()

# Footer
tk.Label(main_frame, text="Password is never stored • Uses k-anonymity (HIBP)",
         font=("Segoe UI", 8), bg=CARD_COLOR, fg="#64748b").pack(pady=(12, 0))

root.mainloop()
