from cs50 import get_string

text = get_string("Text: ")

num_letters = 0
for c in text:
    if c.isalpha():
        num_letters += 1


num_words = len(text.split())

num_sentences = text.count(".") + text.count("!") + text.count("?")

L = num_letters / num_words * 100

S = num_sentences / num_words * 100

grade_level = 0.0588 * L - 0.296 * S - 15.8

if grade_level < 1:
    print("Before Grade 1")
elif grade_level >= 16:
    print("Grade 16+")
else:
    print(f"Grade {round(grade_level)}")
