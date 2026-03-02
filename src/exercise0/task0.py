PHI = 1.618033988749895
import random
import time
import multiprocessing as mp
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class SharedStudent:
    def __init__(self, name, gender, index):
        self.name = name
        self.gender = gender
        self.index = index
        self.state = mp.Manager().Value('s', 'Очередь')
        self.exam_time = mp.Manager().Value('d', 0.0)
    
    def get_name(self):
        return self.name
    
    def get_state(self):
        return self.state.value
    
    def set_state(self, state):
        self.state.value = state
    
    def set_exam_time(self, time_val):
        self.exam_time.value = time_val
    
    def get_exam_time(self):
        return self.exam_time.value
    
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
        if self.gender == 'female': 
            res = n - 1 - res
        return res

class SharedExaminer:
    def __init__(self, name, gender, index):
        self.name = name
        self.gender = gender
        self.index = index
        self.number_of_students = mp.Manager().Value('i', 0)
        self.failed_students = mp.Manager().Value('i', 0)
        self.start_work_time = mp.Manager().Value('i', 0)
        self.end_work_time = mp.Manager().Value('i', 0)
        self.had_lunch = mp.Manager().Value('b', False)
        self.student_now_index = mp.Manager().Value('i', -1)
        self.student_now = None
        self.student_name = mp.Manager().Value('s', '-')

    def get_name(self):
        return self.name
    
    def get_student_now(self):
        return self.student_now
    
    def set_student(self, student):
        self.student_now = student
        if student:
            self.student_now_index.value = student.index
            self.student_name.value = student.get_name()
        else:
            self.student_now_index.value = -1
            self.student_name.value = '-'
    
    def get_student_name(self):
        return self.student_name.value
    
    def get_work_time(self):
        end = time.time() if self.end_work_time.value == 0 else self.end_work_time.value
        return round(end - self.start_work_time.value, 2)
    
    def set_start_work(self):
        self.start_work_time.value = time.time()
    
    def set_end_work(self):
        self.end_work_time.value = time.time()
    
    def sentiment(self) -> int:
        x = random.randint(-2, 5)
        return 1 if x > 0 else -1 if x < 0 else 0
    
    def add_students_count(self, res):
        self.number_of_students.value += 1
        if not res: 
            self.failed_students.value += 1
    
    def lunch(self):
        self.set_student(None)
        self.had_lunch.value = True
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
        if self.gender == 'female': 
            res = n - 1 - res
        return res
    
    def quests(self, question: list) -> list:
        que = question[::]
        res = []
        for _ in range(len(question)):
            if not que:
                break
            answer = self.quest(que)
            res.append(answer)
            que.pop(answer)
            if random.randint(0, 2) > 0: 
                break
        return res
    
    def get_rate(self) -> float:
        if self.number_of_students.value > 0:
            return (self.number_of_students.value - self.failed_students.value) / self.number_of_students.value
        return 0

def read_persons(filename: str, start_idx=0):
    persons = []
    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            parts = line.strip().split()
            if line and len(parts) == 2:
                if filename == 'students.txt':
                    persons.append(SharedStudent(parts[0], parts[1], start_idx + i))
                else:
                    persons.append(SharedExaminer(parts[0], parts[1], start_idx + i))
    return persons

def read_questions(filename: str) -> list:
    questions = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():
                questions.append(line.strip().split())
    return questions

def sort_students(students: list) -> list:
    failed = []
    completed = []
    queue = []
    for s in students:
        state = s.get_state()
        if state == "Провалил":
            failed.append(s)
        elif state == "Сдал":
            completed.append(s)
        else:
            queue.append(s)
    return queue + completed + failed

def exam_output(students, examiners, time_val, q_size, lock_display):
    with lock_display:
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[H", end="")
        
        students_copy = list(students)
        examiners_copy = list(examiners)
        
        stud = sort_students(students_copy)
        max_name_len = max(7, max((len(s.get_name()) for s in students_copy), default=0))
        print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
        print('| ' + 'Студент'.ljust(max_name_len) + ' |  Статус  |')
        print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
        for s in stud:
            name = s.get_name().ljust(max_name_len)
            state = s.get_state().center(10)
            print(f'| {name} |{state}|')
        print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
        print()
        
        max_len_names = max(11, max((len(e.get_name()) for e in examiners_copy), default=0))
        print('+' + '-' * (max_len_names + 2) + 
              '+-----------------+-----------------+---------+--------------+')
        print('| ' + 'Экзаменатор'.ljust(max_len_names) + 
              ' | Текущий студент | Всего студентов | Завалил | Время работы |')
        print('+' + '-' * (max_len_names + 2) + 
              '+-----------------+-----------------+---------+--------------+')
        
        for e in examiners_copy:
            name = e.get_name().ljust(max_len_names)
            student_name = e.get_student_name().center(17)
            total_students = str(e.number_of_students.value).center(17)
            failed_students = str(e.failed_students.value).center(9)
            work_time = (str(e.get_work_time())).center(14)
            
            print(f'| {name} |{student_name}|{total_students}|{failed_students}|{work_time}|')
        print('+' + '-' * (max_len_names + 2) + 
              '+-----------------+-----------------+---------+--------------+')
        
        with q_size.get_lock():
            current_size = q_size.value
        print('Осталось в очереди: ' + str(min(current_size, len(students_copy))) + ' из ' + str(len(students_copy)))
        print('Время с момента начала экзамена:', round(time_val, 2))

def output_every_second(start_time, students, examiners, q_size, exit_event, lock_display):
    last_update = 0
    while not exit_event.is_set():
        current_time = time.time()
        if current_time - last_update >= 0.1:  # Увеличил до 0.1 для уменьшения нагрузки
            last_update = current_time
            exam_output(students, examiners, current_time - start_time, q_size, lock_display)
        time.sleep(0.05)

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
        total_students = str(e.number_of_students.value).center(17)
        failed_students = str(e.failed_students.value).center(9)
        work_time = str(e.get_work_time()).center(14)
        
        print(f'| {name} |{total_students}|{failed_students}|{work_time}|')
    print('+' + '-' * (max_len_names + 2) + 
          '+-----------------+---------+--------------+')

def examiner_work(examiner, student_queue, questions, good_questions, lock_good, lock_qsize, q_size, exit_event):
    examiner.set_start_work()
    
    while not exit_event.is_set():
        try:
            student = student_queue.get(timeout=0.5)
            if student is None:
                break
        except:
            continue
        
        examiner.set_student(student)
        
        # Проводим экзамен
        res = examiner.sentiment()
        question_indices = list(range(len(questions)))
        
        for _ in range(3):
            if not question_indices:
                break
            j = random.choice(question_indices)
            question_indices.remove(j)
            
            student_answer = student.quest(questions[j])
            examiner_answer = examiner.quests(questions[j])
            
            if student_answer in examiner_answer:
                with lock_good:
                    good_questions[j] += 1
                res *= 10
        
        # Определяем результат
        passed = res < 0 or res > 99
        
        # Имитируем время экзамена
        time.sleep(random.uniform(len(examiner.get_name()) - 1, len(examiner.get_name()) + 1))
        
        # Обновляем состояние
        student.set_state('Сдал' if passed else 'Провалил')
        student.set_exam_time(time.time())
        examiner.add_students_count(passed)
        
        with lock_qsize:
            q_size.value -= 1
        
        # Проверяем обед
        if examiner.get_work_time() > 30 and not examiner.had_lunch.value:
            examiner.lunch()
    examiner.set_student(None)
    examiner.set_end_work()

def results(students, examiners, good_questions, questions):
    best_students = []
    worst_students = []
    best_examiners = []
    best_questions = []
    
    best_exam_time = float('inf')
    worst_exam_time = float('inf')
    best_exam_rate = 0
    failed_students = 0
    
    for s in students:
        if s.get_state() == 'Сдал':
            if s.get_exam_time() < best_exam_time:
                best_exam_time = s.get_exam_time()
        else:
            if s.get_exam_time() < worst_exam_time:
                worst_exam_time = s.get_exam_time()
            failed_students += 1
    
    for e in examiners:
        rate = e.get_rate()
        if rate > best_exam_rate:
            best_exam_rate = rate
    
    for s in students:
        if s.get_state() == 'Сдал':
            if s.get_exam_time() == best_exam_time:
                best_students.append(s)
        else:
            if s.get_exam_time() == worst_exam_time:
                worst_students.append(s)
    
    for e in examiners:
        if e.get_rate() == best_exam_rate:
            best_examiners.append(e)
    
    if good_questions and questions:
        best_question_rate = max(good_questions)
        for i in range(len(good_questions)):
            if good_questions[i] == best_question_rate:
                best_questions.append(questions[i])
    
    success_rate = (len(students) - failed_students) / len(students) if students else 0
    ex_res = 'экзамен удался' if success_rate > 0.85 else 'экзамен не удался'
    
    return best_students, worst_students, best_examiners, best_questions, ex_res

def final_output(students, examiners, total_time, questions, good_questions):
    best_students, worst_students, best_examiners, best_questions, ex_res = results(students, examiners, good_questions, questions)
    stud = sort_students(students)
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    
    max_name_len = max(7, max((len(s.get_name()) for s in students), default=0))
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
    print('| ' + 'Студент'.ljust(max_name_len) + ' |  Статус  |')
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
    for s in stud:
        name = s.get_name().ljust(max_name_len)
        state = s.get_state().center(10)
        print(f'| {name} |{state}|')
    print('+' + '-' * (max_name_len + 2) + '+' + '-' * 10 + '+')
    print()
    
    print_examiners_final(examiners)
    print()
    print(f"Время с момента начала экзамена и до момента и его завершения: {total_time}")
    print("Имена лучших студентов:", ', '.join([s.get_name() for s in best_students]) if best_students else "нет")
    print("Имена лучших экзаменаторов: ", ', '.join([e.get_name() for e in best_examiners]) if best_examiners else "нет")
    print("Имена студентов, которых после экзамена отчислят: ", ', '.join([s.get_name() for s in worst_students]) if worst_students else "нет")
    print("Лучшие вопросы: ", ', '.join([' '.join(q) for q in best_questions]) if best_questions else "нет")
    print("Вывод:", ex_res)

def main():
    if sys.platform == 'darwin':
        try:
            mp.set_start_method('fork', force=True)
        except RuntimeError:
            pass
    
    manager = mp.Manager()
    
    students = read_persons("students.txt")
    examiners = read_persons("examiners.txt", len(students))
    questions = read_questions("questions.txt")
    
    good_questions = mp.Array('i', [0] * len(questions))
    lock_good = mp.Lock()
    lock_qsize = mp.Lock()
    lock_display = mp.Lock()
    
    student_queue = mp.Queue()
    for student in students:
        student_queue.put(student)
    for _ in examiners:
        student_queue.put(None)
    
    q_size = mp.Value('i', len(students))
    exit_event = mp.Event()
    start_time = time.time()
    
    examiner_processes = []
    for ex in examiners:
        p = mp.Process(
            target=examiner_work,
            args=(ex, student_queue, questions, good_questions, 
                  lock_good, lock_qsize, q_size, exit_event)
        )
        p.start()
        examiner_processes.append(p)
    
    output_process = mp.Process(
        target=output_every_second,
        args=(start_time, students, examiners, q_size, exit_event, lock_display)
    )
    output_process.start()
    
    for p in examiner_processes:
        p.join()
    
    exit_event.set()
    output_process.join()
    
    total_time = round(time.time() - start_time, 2)
    final_output(students, examiners, total_time, questions, good_questions[:])

if __name__ == '__main__':
    main()