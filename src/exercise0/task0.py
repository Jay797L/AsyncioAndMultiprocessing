PHI = 1.618033988749895
import random
import time
import threading
import queue
import os
import copy

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

best_exam_time = None
worst_exam_time = None
best_exam_rate = None
failed_students = 0

class Student:
    name: str
    gender: str
    state: str = 'Очередь'
    exam_time: float = 0

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    def get_name(self):
        return self.name
    
    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state

    def set_exam_time(self, time: float):
        self.exam_time = time

    def get_exam_time(self):
        return self.exam_time

    def quest(self, question: list) -> int:
        rand_num = random.random()
        probabilities = []
        n = len(question)
        res = n - 1
        for i in range(n):    
            probabilities.append((1-sum(probabilities))/PHI)
            if rand_num < sum(probabilities):
                res = i
                break
        if self.gender == 'female': res = n - 1 - res
        return res





class Examiner:
    name: str
    gender: str
    state: str = '-'
    number_of_students: int = 0
    failed_students: int = 0
    start_work_time: int = 0
    end_work_time: int = None
    student_now: Student = None
    had_lunch: bool = False

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
        return '-' if self.student_now is None else self.student_now.get_name()
    
    def get_work_time(self):
        return (int(time.time()) if self.end_work_time is None else self.end_work_time) - self.start_work_time
    
    def set_start_work(self):
        self.start_work_time = int(time.time())

    def set_end_work(self):
        self.end_work_time = int(time.time())
    
    def sentiment(self) -> int:
        x = random.randint(-2, 5)
        res = 1 if x > 0 else -1 if x < 0 else 0
        return res
    
    def add_students_count(self, res):
        self.number_of_students += 1
        if not res: self.failed_students += 1
    
    def lunch(self, update_q):
        self.set_student(None)
        self.had_lunch = True
        update_q.put(True)
        time.sleep(random.uniform(12, 18))

    def quest(self, question: list) -> int:
        rand_num = random.random()
        probabilities = []
        n = len(question)
        res = n - 1
        for i in range(n):    
            probabilities.append((1-sum(probabilities))/PHI)
            if rand_num < sum(probabilities):
                res = i
                break
        if self.gender == 'female': res = n - 1 - res
        return res

    def quests(self, question: list) -> list:
        que = question[::]
        res = []
        for _ in range(len(question)):
            answer = self.quest(que)
            res.append(answer)
            que.pop(answer)
            if random.randint(0, 2) > 0: break
        return res

    def get_rate(self) -> float:
        return self.number_of_students/ self.failed_students




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



def sort_students(students: list) -> list:
    failed = []
    completed = []
    queue = []
    std = copy.deepcopy(students)
    for i in std:
        if i.get_state() == "Провалил":
            failed.append(i)
        elif i.get_state() == "Сдал":
            completed.append(i)
        else:
            queue.append(i)
    return queue + completed + failed



def exam_output(students: list, examiners: list, time: int, student_queue):
    stud = sort_students(students)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H", end="")
    # os.system('cls' if os.name == 'nt' else 'clear')
    print_student_exam(stud)
    print()
    print_examiners_exam(examiners)
    print('Осталось в очереди: ' + str(min(student_queue.qsize(), len(stud))) + ' из ' + str(len(stud)))
    print('Время с момента начала экзамена: ' + str(time//60) + '.' + str(time%60))


def print_student_exam(students: list):
    max_name_len = max(7, max((len(s.get_name()) for s in students), default=0))
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
    print('| ' + 'Студент'.ljust(max_name_len) + ' |  Статус  |')
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
    for s in students:
        name = s.get_name().ljust(max_name_len)
        state = s.get_state().center(10)
        print(f'| {name} |{state}|')
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')

def print_examiners_exam(examiners: list):
    max_len_names = max(11, max((len(e.get_name()) for e in examiners), default=0))
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')
    print('| ' + 'Экзаменатор'.ljust(max_len_names) + 
          ' | Текущий студент | Всего студентов | Завалил | Время работы |')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')

    for e in examiners:
        name = e.get_name().ljust(max_len_names)
        student_name = e.get_student_name().center(17)
        total_students = str(e.number_of_students).center(17)
        failed_students = str(e.failed_students).center(9)
        work_time = (str(e.get_work_time()//60) + '.' + str(e.get_work_time()%60)).center(14)
        
        print(f'| {name} |{student_name}|{total_students}|{failed_students}|{work_time}|')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+-----------------+---------+--------------+')
    
def print_examiners_final(examiners: list):
    max_len_names = max(11, max((len(e.get_name()) for e in examiners), default=0))
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+---------+--------------+')
    print('| ' + 'Экзаменатор'.ljust(max_len_names) + 
          ' | Всего студентов | Завалил | Время работы |')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+---------+--------------+')

    for e in examiners:
        name = e.get_name().ljust(max_len_names)
        total_students = str(e.number_of_students).center(17)
        failed_students = str(e.failed_students).center(9)
        work_time = (str(e.get_work_time()//60) + '.' + str(e.get_work_time()%60)).center(14)
        
        print(f'| {name} |{total_students}|{failed_students}|{work_time}|')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+---------+--------------+')


def output_every_second(t: dict, students: list, examiners: list, student_queue, update_q):
    exam_output(students, examiners, 0, student_queue)
    while(student_queue.qsize()):
        current_time = time.time()
        if(current_time - t['update_time'] >= 1 or update_q.qsize() > 0):
            while update_q.qsize() > 0: update_q.get()
            t['update_time'] = current_time
            # os.system('cls' if os.name == 'nt' else 'clear')
            exam_output(students, examiners, int(t['update_time'] - t['start_time']), student_queue)





def final_output(students: list, examiners: list, total_time: int):
    best_students, worst_students, best_examiners, best_questions, ex_res = results(students, examiners, good_questions, questions)
    stud = sort_students(students)
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    print_student_exam(stud)
    print()
    print_examiners_final(examiners)
    print()
    print("Время с момента начала экзамена и до момента и его завершения: ", total_time//60, ':', total_time%60, sep = '')
    print("Имена лучших студентов:", str(best_students)[1:-1])
    print("Имена лучших экзаменаторов: ", str(best_examiners)[1:-1])
    print("Имена студентов, которых после экзамена отчислят: ", str(worst_students)[1:-1])
    print("Лучшие вопросы: ", str(best_questions)[1:-1])
    print("Вывод:", ex_res)





def examiner_work(examiner: Examiner, student_queue, questions: list, update_q, good_questions: list):
    examiner.set_start_work()
    examiner.set_student(student_queue.get())
    while(examiner.get_student_name() != '-'):
        res = examiner.sentiment()
        que = questions[::]
        for _ in range(3):
            j = random.randint(0, len(que)-1)
            student_answer = examiner.get_student_now().quest(que[j])
            examiner_answer = examiner.quests(que[j])
            x = que.pop(j)
            if student_answer in examiner_answer:
                good_questions[questions.index(x)] += 1
                res *= 10
        res = res < 0 or res > 99
        time.sleep(random.uniform(len(examiner.get_name()) - 1, len(examiner.get_name()) + 1))
        examiner.get_student_now().set_state('Сдал' if res else 'Провалил')
        examiner.add_students_count(res)

        if examiner.get_work_time() > 30 and not examiner.had_lunch:
            examiner.lunch(update_q)
        examiner.set_student(student_queue.get())
        update_q.put(True)
    examiner.set_end_work()

def results(students: list, examiners: list, good_questions: list, questions: list) -> tuple:
    best_students = []
    worst_students = []
    best_examiners = []
    best_questions = []

    for s in students:
        if s.get_state() == 'Сдал':
            if best_exam_time is None or s.get_exam_time() < best_exam_time: best_exam_time = s.get_exam_time()
        else:
            if worst_exam_time is None or s.get_exam_time() < worst_exam_time: worst_exam_time = s.get_exam_time()

    for e in examiners:
        if best_exam_rate is None or best_exam_rate < e.get_rate(): best_exam_rate = e.get_rate()

    for s in students:
        if s.get_state() == 'Сдал':
            if s.get_exam_time() == best_exam_time: best_students.append(s)
        else:
            if s.get_exam_time() == worst_exam_time: worst_students.append(s)

    for e in examiners:
        if best_exam_rate == e.get_rate(): best_examiners.append(e)

    best_question_rate = max(good_questions)
    for i in range(len(good_questions)):
        if good_questions[i] == best_question_rate: best_questions.append(questions[i])

    ex_res = 'экзамен удался' if (len(students) - failed_students) / len(students) > 0.85 else 'экзамен не удался'

    return best_students, worst_students, best_examiners, best_questions, ex_res

def main():

    examiners = read_persons("examiners.txt")
    students = read_persons("students.txt")
    questions = read_questions("questions.txt")
    good_questions = questions[::]
    for i in good_questions: i = 0

    update_q = queue.Queue()
    student_queue = queue.Queue()
    for student in students:
        student_queue.put(student)
    for _ in examiners:
        student_queue.put(None)

    t = {'start_time': time.time(), 'update_time': -1}

    threads = [threading.Thread(target = examiner_work, args = (ex, student_queue, questions, update_q, good_questions)) for ex in examiners]
    output_thread = threading.Thread(target = output_every_second, args = (t, students, examiners, student_queue, update_q))
    
    output_thread.start()
    for i in threads: i.start()
    for i in threads: i.join()
    output_thread.join()

    total_time = round(int(time.time() - t['start_time']))
    final_output(students, examiners, total_time)

if __name__ == '__main__':
    main()