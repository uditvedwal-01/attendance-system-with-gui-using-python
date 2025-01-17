import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

# File paths
STUDENT_DB = "students_database.txt"
TEACHER_DB = "teachers_database.txt"

# Get current date
def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")

# Authenticate teacher
def authenticate_teacher(teacher_id, password):
    try:
        with open(TEACHER_DB, "r") as file:
            for line in file:
                id_, pass_, section, course, name = line.strip().split(",")
                if id_ == teacher_id and pass_ == password:
                    return section, course, name
    except FileNotFoundError:
        messagebox.showerror("Error", "Teacher database file not found!")
    return None, None, None

# Get student details
def get_student_details(roll_number):
    try:
        with open(STUDENT_DB, "r") as file:
            for line in file:
                details = line.strip().split(",")
                if details[0] == roll_number:
                    return details
    except FileNotFoundError:
        messagebox.showerror("Error", "Student database file not found!")
    return None

# Mark attendance
def mark_attendance(roll_number, password):
    student_details = get_student_details(roll_number)
    if not student_details:
        messagebox.showerror("Error", f"Roll Number {roll_number} not found!")
        return

    if password != student_details[6]:
        messagebox.showerror("Error", "Incorrect password!")
        return

    date = get_current_date()
    section = student_details[3]
    course = student_details[4]
    attendance_file = f"{section}_{course}_{date}.txt"

    # Check if attendance already marked
    if os.path.exists(attendance_file):
        with open(attendance_file, "r") as file:
            if any(roll_number in line for line in file):
                messagebox.showinfo("Info", f"Attendance already marked for Roll Number {roll_number}.")
                return

    # Mark attendance
    with open(attendance_file, "a") as file:
        file.write(f"{student_details[0]},{student_details[1]},{student_details[2]}\n")
    messagebox.showinfo("Success", f"Attendance marked for Roll Number {roll_number}.")

# View past attendance for a student
def view_student_past_attendance(roll_number):
    attendance_records = []
    files = [file for file in os.listdir() if file.endswith(".txt") and not file.startswith("students_database")]

    for file in files:
        with open(file, "r") as f:
            for line in f:
                if roll_number in line:
                    attendance_records.append(f"{file.replace('.txt', '')}: {line.strip()}")

    return attendance_records

# View attendance for a specific date
def view_attendance(section, course, date):
    attendance_file = f"{section}_{course}_{date}.txt"
    if not os.path.exists(attendance_file):
        messagebox.showinfo("Info", f"No attendance found for {date}.")
        return []

    with open(attendance_file, "r") as file:
        return file.readlines()

# View absent students
def view_absent_students(section, course):
    date = get_current_date()
    attendance_file = f"{section}_{course}_{date}.txt"
    marked_students = set()

    if os.path.exists(attendance_file):
        with open(attendance_file, "r") as file:
            for line in file:
                roll_number = line.split(",")[0]
                marked_students.add(roll_number)

    all_students = []
    absent_students = []
    try:
        with open(STUDENT_DB, "r") as file:
            for line in file:
                details = line.strip().split(",")
                if details[3] == section and details[4] == course:
                    all_students.append(details)
                    if details[0] not in marked_students:
                        absent_students.append(details)
    except FileNotFoundError:
        messagebox.showerror("Error", "Student database file not found!")

    return absent_students

# Student GUI
def student_login():
    roll_number = simpledialog.askstring("Student Login", "Enter your University Roll Number:")
    password = simpledialog.askstring("Student Login", "Enter your Password:", show="*")

    if not roll_number or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    def mark_attendance_gui():
        mark_attendance(roll_number, password)

    def view_past_attendance_gui():
        attendance_records = view_student_past_attendance(roll_number)
        if attendance_records:
            records = "\n".join(attendance_records)
            messagebox.showinfo("Attendance Records", records)
        else:
            messagebox.showinfo("Attendance Records", "No attendance records found.")

    student_window = tk.Toplevel()
    student_window.title("Student Portal")
    tk.Label(student_window, text="Welcome, Student!", font=("Arial", 16)).pack(pady=10)
    tk.Button(student_window, text="Mark Attendance", command=mark_attendance_gui, width=20).pack(pady=5)
    tk.Button(student_window, text="View Past Attendance", command=view_past_attendance_gui, width=20).pack(pady=5)

# Teacher GUI
def teacher_login():
    teacher_id = simpledialog.askstring("Teacher Login", "Enter your Teacher ID:")
    password = simpledialog.askstring("Teacher Login", "Enter your Password:", show="*")

    if not teacher_id or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    section, course, name = authenticate_teacher(teacher_id, password)
    if not section or not course:
        messagebox.showerror("Error", "Invalid Teacher ID or Password!")
        return

    def view_today_attendance():
        attendance = view_attendance(section, course, get_current_date())
        if attendance:
            messagebox.showinfo("Today's Attendance", "\n".join(attendance))
        else:
            messagebox.showinfo("Today's Attendance", "No attendance marked today.")

    def view_absent_students_gui():
        absent_students = view_absent_students(section, course)
        if absent_students:
            absent_list = "\n".join([f"{s[0]} - {s[2]}" for s in absent_students])
            messagebox.showinfo("Absent Students", absent_list)
        else:
            messagebox.showinfo("Absent Students", "No absent students.")

    def view_past_attendance_gui():
        date = simpledialog.askstring("View Past Attendance", "Enter the date (DD-MM-YYYY):")
        if not date:
            return
        attendance = view_attendance(section, course, date)
        if attendance:
            messagebox.showinfo(f"Attendance on {date}", "\n".join(attendance))
        else:
            messagebox.showinfo(f"Attendance on {date}", "No attendance marked on this date.")

    teacher_window = tk.Toplevel()
    teacher_window.title("Teacher Portal")
    tk.Label(teacher_window, text=f"Welcome, {name}!", font=("Arial", 16)).pack(pady=10)
    tk.Button(teacher_window, text="View Today's Attendance", command=view_today_attendance, width=25).pack(pady=5)
    tk.Button(teacher_window, text="View Absent Students", command=view_absent_students_gui, width=25).pack(pady=5)
    tk.Button(teacher_window, text="View Past Attendance", command=view_past_attendance_gui, width=25).pack(pady=5)

# Main GUI
def main():
    root = tk.Tk()
    root.title("Automated Attendance System")

    tk.Label(root, text="Attendance Management System", font=("Arial", 20)).pack(pady=20)

    tk.Button(root, text="Student Login", command=student_login, width=20).pack(pady=10)
    tk.Button(root, text="Teacher Login", command=teacher_login, width=20).pack(pady=10)
    tk.Button(root, text="Exit", command=root.destroy, width=20).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
