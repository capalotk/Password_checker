import tkinter as tk
from tkinter import messagebox
import re
import hashlib
import requests
from datetime import datetime

def password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 1
    else:
        feedback.append("At least 12 characters")

    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Use both uppercase and lowercase letters")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Include numbers")

    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
    else:
        feedback.append("Include special characters")

    return score, feedback

def check_pwned(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    hashes = (line.split(':') for line in response.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)
    return 0

def save_password(password):
    with open("strong_passwords.txt", "a") as file:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{now}] {password}\n")

def evaluate_password():
    pwd = entry.get()
    if not pwd:
        messagebox.showwarning("Input Error", "Please enter a password.")
        return

    score, feedback = password_strength(pwd)
    breach_count = check_pwned(pwd)

    # Strength message
    strength_msg = f"Score: {score}/4\n"
    if score == 4:
        strength_msg += "✅ Strong Password"
    elif score == 3:
        strength_msg += "⚠️ Moderate Password"
    else:
        strength_msg += "❌ Weak Password"
    result_strength.config(text=strength_msg)

    # Feedback tips
    result_feedback.config(text="\n".join(f"- {f}" for f in feedback) if feedback else "")

    # Breach check
    if breach_count > 0:
        breach_msg = f"❌ Found in {breach_count:,} breaches"
    else:
        breach_msg = "✅ Not found in breaches"
    result_breach.config(text=breach_msg)

    # Save password if strong and not breached
    if score == 4 and breach_count == 0:
        save_password(pwd)
        messagebox.showinfo("Saved", "✅ Strong password saved to 'strong_passwords.txt'")

# --- GUI Setup ---
window = tk.Tk()
window.title("Password Strength Checker")
window.geometry("420x330")
window.resizable(False, False)

tk.Label(window, text="Enter Password:", font=("Arial", 12)).pack(pady=10)

entry = tk.Entry(window, width=30, font=("Arial", 12))  # no masking here
entry.pack()

tk.Button(window, text="Check Password", command=evaluate_password, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=10)

result_strength = tk.Label(window, text="", font=("Arial", 11, "bold"))
result_strength.pack()

result_feedback = tk.Label(window, text="", fg="red", font=("Arial", 10))
result_feedback.pack()

result_breach = tk.Label(window, text="", font=("Arial", 11))
result_breach.pack(pady=5)

window.mainloop()
