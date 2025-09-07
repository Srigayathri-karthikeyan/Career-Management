import mysql.connector
from tkinter import *
from tkinter import messagebox

answers = {
    1: {'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6, 'F': 7},
    2: {'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6, 'F': 7},
    3: {'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6},
    4: {'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6, 'F': 7, 'G': 8, 'H': 9, 'I': 10, 'J': 11, 'K': 12, 'L': 13},
    5: {'A': 2, 'B': 3, 'C': 4, 'D': 5},
    6: {'A': 2, 'B': 3, 'C': 4, 'D': 5},
    7: {'A': 2, 'B': 3, 'C': 4, 'D': 5},
    8: {'A': 2, 'B': 3, 'C': 4, 'D': 5},
}

def create_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_data;")
        cursor.execute("USE student_data;")

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            age INT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id VARCHAR(255),
            question_number INT,
            question TEXT,
            response CHAR(1),
            FOREIGN KEY(id) REFERENCES students(id) ON DELETE CASCADE
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_suggestions (
            id VARCHAR(255),
            career TEXT,
            FOREIGN KEY(id) REFERENCES students(id)
        )
        ''')

        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def read_questions():
    questions = []
    try:
        with open("Questionbank.txt", "r") as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
                question = lines[i].strip()
                options = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    options.append(lines[i].strip())
                    i += 1
                questions.append({"question": question, "options": options})
                i += 1
    except FileNotFoundError:
        messagebox.showerror("Error", "Questionbank.txt file not found.")
    return questions

def save_student_details(student_id, name, age):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="student_data"
        )
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO students (id, name, age) VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), age = VALUES(age)
        ''', (student_id, name, age))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")


def save_responses(student_id, responses):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="student_data"
        )
        cursor = conn.cursor()
        for question, response, question_number in responses:
            cursor.execute("INSERT INTO responses (id, question_number,question, response) VALUES (%s, %s, %s, %s)", 
                           (student_id, question_number,question, response))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

def save_career_suggestion(student_id, career):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="student_data"
        )
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO career_suggestions (id, career) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE career = VALUES(career)
        ''', (student_id, career))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

def assign_career(score):
    if 16 <= score <= 24:
        return "Healthcare, Education, Social Services"
    elif 25 <= score <= 32:
        return "Engineering, Technology, IT"
    elif 33 <= score <= 40:
        return "Business, Management, Entrepreneurship"
    elif 41 <= score <= 48:
        return "Arts, Design, Creativity"
    elif 49 <= score <= 56:
        return "Science, Research, Environment"
    elif 57 <= score <= 64:
        return "Law, Politics, Government"
    else:
        return "Unknown"

def start_counseling(root, student_details, questions):
    for widget in root.winfo_children():
        widget.destroy()

    current_question = 0
    total_score = 0
    responses = []
    selected_option = StringVar()

    def display_question():
        nonlocal current_question, total_score, responses

        for widget in root.winfo_children():
            widget.destroy()

        if current_question >= len(questions):
            career = assign_career(total_score)
            messagebox.showinfo("Result", f"Total Score: {total_score}\nSuggested Career: {career}")
            save_responses(student_details["id"], responses)
            save_career_suggestion(student_details["id"], career)
            root.quit()
            return

        question_data = questions[current_question]
        Label(root, text=question_data["question"], font=("Arial", 14)).pack(pady=10)
        selected_option.set(None)
        for option in question_data["options"]:
            Radiobutton(root, text=option, value=option[0], variable=selected_option).pack(anchor="w")

        Button(root, text="Next", command=next_question).pack(pady=20)

    def next_question():
        nonlocal current_question, total_score, responses

        if not selected_option.get():
            messagebox.showwarning("Warning", "Please select an option.")
            return

        responses.append((questions[current_question]["question"], selected_option.get(), current_question + 1))
        current_question_number = current_question + 1
        total_score += answers.get(current_question_number, {}).get(selected_option.get(), 0)
        current_question += 1
        display_question()

    display_question()

def display_student_info_form(root, questions):
    Label(root, text="Enter Student ID:").pack(pady=5)
    id_entry = Entry(root)
    id_entry.pack(pady=5)

    Label(root, text="Enter Your Name:").pack(pady=5)
    name_entry = Entry(root)
    name_entry.pack(pady=5)

    Label(root, text="Enter Your Age:").pack(pady=5)
    age_entry = Entry(root)
    age_entry.pack(pady=5)

    def submit_details():
        student_id = id_entry.get().strip()
        name = name_entry.get().strip()
        age = age_entry.get().strip()

        if not student_id or not name or not age.isdigit():
            messagebox.showwarning("Input Error", "Please enter valid details.")
            return

        save_student_details(student_id, name, int(age))
        start_counseling(root, {"id": student_id, "name": name, "age": int(age)}, questions)

    Button(root, text="Submit", command=submit_details).pack(pady=20)

if __name__ == "__main__":
    create_database()
    root = Tk()
    root.title("Career Counseling App")
    root.geometry("500x400")
    questions = read_questions()
    display_student_info_form(root, questions)
    root.mainloop()
