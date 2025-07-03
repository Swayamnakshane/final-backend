import json
import random
from datetime import datetime

# Topics to cover for hard-level Python coding MCQs
topics = [
    "Recursion", "OOP", "Closures", "Decorators", "Generators", "Context Managers",
    "Metaclasses", "Descriptors", "Multithreading", "Multiprocessing", "Error Handling",
    "Function Overloading", "Custom Exceptions", "File Handling", "Regex", "List Comprehension",
    "Dictionary Comprehension", "Set Operations", "Itertools", "Dataclasses"
]

# Generate one MCQ
def generate_hard_mcq(q_id):
    code_templates = {
        "Recursion": """
def mystery(n):
    if n <= 1:
        return 1
    return n * mystery(n - 1)

print(mystery(5))
""",
        "OOP": """
class A:
    def __init__(self):
        self.val = 5

    def __str__(self):
        return str(self.val)

a = A()
print(a)
""",
        "Closures": """
def outer(x):
    def inner(y):
        return x + y
    return inner

add_five = outer(5)
print(add_five(10))
""",
        "Decorators": """
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) * 2
    return wrapper

@decorator
def add(x, y):
    return x + y

print(add(3, 4))
""",
        "Generators": """
def count_up_to(n):
    i = 0
    while i < n:
        yield i
        i += 2

gen = count_up_to(5)
print(next(gen))
print(next(gen))
""",
        "Context Managers": """
class Manager:
    def __enter__(self):
        print("Enter")
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exit")

with Manager():
    print("Inside block")
""",
        "Error Handling": """
try:
    result = 10 / 0
except ZeroDivisionError:
    result = 'Infinity'
finally:
    print("Done")

print(result)
""",
        "File Handling": """
with open("test.txt", "w") as f:
    f.write("Line1\\nLine2")
with open("test.txt", "r") as f:
    lines = f.readlines()
print(lines[1])
""",
        "Regex": """
import re
text = "My phone number is 9876543210"
match = re.search(r"\\d{10}", text)
print(match.group())
""",
        "Dataclasses": """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(2, 3)
print(p.x + p.y)
"""
    }

    topic = random.choice(topics)
    code = code_templates.get(topic, list(code_templates.values())[0])
    options = [
        "Correct output is printed",
        "An error occurs during execution",
        "Unexpected output due to logic error",
        "Program crashes silently"
    ]
    correct_answer = "A"
    return {
        "id": q_id,
        "question": f"What will be the output of the following code?\n\n{code.strip()}",
        "options": [f"{chr(65 + i)}: {opt}" for i, opt in enumerate(options)],
        "answer": correct_answer,
        "topic": topic,
        "difficulty": "Hard",
        "created_at": datetime.now().isoformat()
    }

# Generate 300 hard-level questions
hard_mcqs = [generate_hard_mcq(i + 1) for i in range(300)]

# Save to JSON file
file_path = "hard_python_coding_mcqs.json"
with open(file_path, "w") as f:
    json.dump(hard_mcqs, f, indent=2)

file_path
