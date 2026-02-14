PHI = 1.618033988749895
import random
import time
import threading
import queue
from datetime import datetime
from collections import defaultdict
import sys


class Student:
    name: str
    gender: str
    state: str = ' Очередь  '

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    def get_name(self):
        return self.name
    def get_state(self):
        return self.state

class Examiner:
    name: str
    gender: str
    state: str = '-'
    number_of_students: int = 0
    failed_students: int = 0
    work_time: int = 0
    student_now: Student = None

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
    def set_student(self, student):
        self.student_now = student
    def get_name(self):
        return self.name
    def get_state(self):
        return self.state
    def get_student_now(self):
        return self.student_now
    def get_student_name(self):
        return '-' if self.student_now == None else self.student_now.get_name()
    def sentiment(self) -> int:
        return random.randint(-1, 1)

def read_persons(filename: str) -> list:
    persons = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip()
            parts = parts.split()
            if line and len(parts) == 2:
                persons.append(Student(parts[0], parts[1]) if filename == 'students.txt' else Examiner(parts[0], parts[1]))
    return persons

def read_questions(filename: str) -> list:
    questions = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line:
                questions.append(list(line.split()))
    return questions

def exam_output(students: list, examiners: list, time: float, student_queue):
    while len(student_queue):
        print_student_exam(students)
        print()
        print_examiners_exam(examiners)
        print('Осталось в очереди: ' + len(student_queue) + ' из ' + len(students))
        print('Время с момента начала экзамена: ' + time)

def print_student_exam(students: list):
    max_len = max(7, (len(s.get_name()) for s in students))
    print('+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')
    print('| ' + 'Студент' + ' ' * (max_len - 7) + ' |  Статус  |')
    print('+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')
    for s in students:
        print('| ' + s.get_name() + ' ' * (max_len - len(s.get_name)) + ' |' + s.get_state() + '|')
    print('+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')

def print_examiners_exam(examiners: list):
    if not examiners:
        print("Нет экзаменаторов")
        return
    
    max_len_names = max(11, max((len(e.get_name()) for e in examiners), default=0))
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')
    print('| ' + 'Экзаменатор'.ljust(max_len_names) + 
          ' | Текущий студент | Всего студентов | Завалил | Время работы |')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')

    for e in examiners:
        name = e.get_name().ljust(max_len_names)
        student_name = e.get_student_name().center(15)
        total_students = str(e.number_of_students).center(17)
        failed_students = str(e.failed_students).center(9)
        work_time = f"{e.work_time:.2f}".center(14)
        
        print(f'| {name} |{student_name}|{total_students}|{failed_students}|{work_time}|')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')

def final_output(students: list, examiners: list):
    print_student_exam(students)
    print()
    print_examiners_exam(examiners)
    print()
    print("Время с момента начала экзамена и до момента и его завершения: ")
    print("Имена лучших студентов: ")
    print("Имена лучших экзаменаторов: ")
    print("Имена студентов, которых после экзамена отчислят: ")
    print("Лучшие вопросы: ")
    print("Вывод: ")

def examiner_work(examiner: Examiner, student_queue, questions):
    # start_time = time.time()
    examiner.set_student(student_queue.get())
    while(examiner.get_student_name() != None):
        with threading.Lock():
            print(examiner.get_name(), ' ', examiner.get_student_name())
        time.sleep(3)
        with threading.Lock():
            print(examiner.get_name(), ' ', examiner.get_student_name(), ' сдал')
            examiner.set_student(student_queue.get())
        

def main():

    examiners = read_persons("examiners.txt")
    students = read_persons("students.txt")
    questions = read_questions("questions.txt")

    print(questions)
    for ex in examiners:
        print(ex.get_name())
    print
    for st in students:
        print(st.get_name())

    student_queue = queue.Queue()

    for student in students:
        student_queue.put(student)

    for _ in examiners:
        student_queue.put(None)

    threads = (threading.Thread(target = examiner_work, args = (ex, student_queue, questions)) for ex in examiners)
    # output_thread = threading.Thread(target = exam_output, args = (examiners, students, student_queue))
    
    # output_thread.start()
    for i in threads: i.start()

    for i in threads: i.join()
    # output_thread.join()

if __name__ == '__main__':
    main()