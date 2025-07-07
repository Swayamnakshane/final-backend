import json
import random
from datetime import datetime

# Topics for hard-level Python coding MCQs
topics = [
    "Recursion", "OOP", "Closures", "Decorators", "Generators", "Context Managers",
    "Error Handling", "File Handling", "Regex", "Dataclasses"
]

# Code templates (8 lines each)
code_templates = {
    "Recursion": """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(3))
print(factorial(4))
print(factorial(5))
""",

    "OOP": """
class A:
    def __init__(self):
        self.x = 10

    def display(self):
        print(self.x)

a = A()
a.display()
""",

    "Closures": """
def multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(5), triple(5))
""",

    "Decorators": """
def uppercase(func):
    def wrapper():
        return func().upper()
    return wrapper

@uppercase
def greet():
    return "hello"

print(greet())
""",

    "Generators": """
def countdown(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown(3)
print(next(gen))
print(next(gen))
""",

    "Context Managers": """
class Test:
    def __enter__(self):
        print("Enter")
        return "Inside"
    def __exit__(self, *args):
        print("Exit")

with Test() as val:
    print(val)
""",

    "Error Handling": """
try:
    a = 10
    b = 0
    result = a / b
except ZeroDivisionError:
    print("Division by zero")
else:
    print(result)
finally:
    print("Cleanup done")
""",

    "File Handling": """
with open("sample.txt", "w") as f:
    f.write("Line1\\nLine2\\nLine3")

with open("sample.txt", "r") as f:
    lines = f.readlines()

print(lines[0].strip())
""",

    "Regex": """
import re
text = "Call me at 9123456789 or 8123456780"
pattern = r"\\b\\d{10}\\b"
matches = re.findall(pattern, text)

for num in matches:
    print(num)
""",

    "Dataclasses": """
from dataclasses import dataclass

@dataclass
class Book:
    title: str
    pages: int

b = Book("Python", 300)
print(b.title)
print(b.pages)
"""
}

# Answer style pool
option_phrases = [
    "Code runs and prints correct output",
    "An exception is raised",
    "Nothing is printed",
    "Logical error but no exception",
    "Both A and B",
    "None of the above",
    "Only B is true",
    "Output depends on Python version"
]

# Generate one MCQ
def generate_hard_mcq(q_id):
    topic = random.choice(topics)
    code = code_templates[topic].strip()

    # Pick 3 normal + 1 confusing option
    base_opts = random.sample(option_phrases[:4], 3)
    tricky_opt = random.choice(option_phrases[4:])
    all_opts = base_opts + [tricky_opt]
    random.shuffle(all_opts)

    # Format options A-D
    formatted_options = [f"{chr(65+i)}: {opt}" for i, opt in enumerate(all_opts)]

    # Randomly assign a correct one (placeholder, not evaluated)
    correct_option = random.choice(["A", "B", "C", "D"])

    return {
        "id": q_id,
        "question": f"What will be the output of the following Python code?\n\n{code}",
        "options": formatted_options,
        "answer": correct_option,
        "topic": topic,
        "difficulty": "Hard",
        "created_at": datetime.now().isoformat()
    }

# Generate 300 MCQs
mcqs = [generate_hard_mcq(i + 1) for i in range(300)]

# Save to JSON
with open("hard_python_coding_mcqs.json", "w") as f:
    json.dump(mcqs, f, indent=2)

print("✅ Saved 300 hard-level Python MCQs to 'hard_python_coding_mcqs.json'")
