PHI = 1.618033988749895
import random
import time
import threading
import queue
import curses
import os  

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

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





def print_student_exam(stdscr, students, start_row, start_col):
    """Отрисовка таблицы студентов с помощью curses"""
    if not students:
        return start_row
    
    # Находим максимальную длину имени
    max_len = 7
    for s in students:
        name_len = len(s.get_name())
        if name_len > max_len:
            max_len = name_len
    
    row = start_row
    col = start_col
    
    # Верхняя граница
    stdscr.addstr(row, col, '+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')
    row += 1
    
    # Заголовок
    stdscr.addstr(row, col, '| ' + 'Студент' + ' ' * (max_len - 7 + 2) + '|  Статус  |')
    row += 1
    
    # Разделитель
    stdscr.addstr(row, col, '+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')
    row += 1
    
    # Студенты
    for s in students:
        name = s.get_name()
        state = s.get_state()
        stdscr.addstr(row, col, f'| {name}' + ' ' * (max_len - len(name) + 2) + f'|{state}|')
        row += 1
    
    # Нижняя граница
    stdscr.addstr(row, col, '+' + '-' * (max_len + 2) + "+" + '-' * 10 + '+')
    
    return row + 1  # Возвращаем следующую строку

def print_examiners_exam(stdscr, examiners, start_row, start_col):
    """Отрисовка таблицы экзаменаторов с помощью curses"""
    if not examiners:
        stdscr.addstr(start_row, start_col, "Нет экзаменаторов")
        return start_row + 1
    
    # Находим максимальную длину имени
    max_len_names = 11
    for e in examiners:
        name_len = len(e.get_name())
        if name_len > max_len_names:
            max_len_names = name_len
    
    row = start_row
    col = start_col
    
    # Верхняя граница
    stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                 '+-----------------+-----------------+---------+--------------+')
    row += 1
    
    # Заголовок
    stdscr.addstr(row, col, '| ' + 'Экзаменатор'.ljust(max_len_names) + 
                 ' | Текущий студент | Всего студентов | Завалил | Время работы |')
    row += 1
    
    # Разделитель
    stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                 '+-----------------+-----------------+---------+--------------+')
    row += 1
    
    # Экзаменаторы
    for e in examiners:
        name = e.get_name().ljust(max_len_names)
        student_name = e.get_student_name().center(15)
        total_students = str(e.number_of_students).center(17)
        failed_students = str(e.failed_students).center(9)
        work_time = f"{e.work_time:.2f}".center(14)
        
        stdscr.addstr(row, col, f'| {name} |{student_name}|{total_students}|{failed_students}|{work_time}|')
        row += 1
    
    # Нижняя граница
    stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                 '+-----------------+-----------------+---------+--------------+')
    
    return row + 1

def exam_output(students, examiners, time_elapsed, student_queue):
    """Вывод во время экзамена с использованием curses"""
    # Эта функция будет вызываться из curses_main
    global stdscr, total_students_count
    
    if 'stdscr' not in globals():
        return
    
    stdscr.clear()
    
    # Получаем размеры окна
    height, width = stdscr.getmaxyx()
    
    current_row = 0
    
    # Таблица студентов
    current_row = print_student_exam(stdscr, students, current_row, 0)
    current_row += 1
    
    # Таблица экзаменаторов
    current_row = print_examiners_exam(stdscr, examiners, current_row, 0)
    current_row += 1
    
    # Информация об очереди
    queue_size = 0
    if student_queue:
        queue_size = student_queue.qsize()
        # Корректируем с учетом сигналов None для экзаменаторов
        queue_size = max(0, queue_size - len(examiners))
    
    queue_info = f"Осталось в очереди: {queue_size} из {total_students_count}"
    stdscr.addstr(current_row, 0, queue_info)
    current_row += 1
    
    # Время
    minutes = int(time_elapsed) // 60
    seconds = int(time_elapsed) % 60
    time_str = f"Время с момента начала экзамена: {minutes}.{seconds:02d}"
    stdscr.addstr(current_row, 0, time_str)
    
    # Обновляем экран
    stdscr.refresh()

def final_output(students, examiners, total_time, best_students, best_examiners, expelled_students, best_questions, conclusion):
    """Финальный вывод после завершения экзамена с использованием curses"""
    global stdscr
    
    if 'stdscr' not in globals():
        return
    
    stdscr.clear()
    
    height, width = stdscr.getmaxyx()
    
    current_row = 0
    
    # Таблица студентов
    current_row = print_student_exam(stdscr, students, current_row, 0)
    current_row += 2
    
    # Таблица экзаменаторов
    if examiners:
        # Находим максимальную длину имени для финальной таблицы
        max_len_names = 11
        for e in examiners:
            name_len = len(e.get_name())
            if name_len > max_len_names:
                max_len_names = name_len
        
        row = current_row
        col = 0
        
        # Верхняя граница (финальная таблица без "Текущий студент")
        stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                     '+-----------------+---------+--------------+')
        row += 1
        
        # Заголовок
        stdscr.addstr(row, col, '| ' + 'Экзаменатор'.ljust(max_len_names) + 
                     ' | Всего студентов | Завалил | Время работы |')
        row += 1
        
        # Разделитель
        stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                     '+-----------------+---------+--------------+')
        row += 1
        
        # Экзаменаторы
        for e in examiners:
            name = e.get_name().ljust(max_len_names)
            total_students = str(e.number_of_students).center(17)
            failed_students = str(e.failed_students).center(9)
            work_time = f"{e.work_time:.2f}".center(14)
            
            stdscr.addstr(row, col, f'| {name} |{total_students}|{failed_students}|{work_time}|')
            row += 1
        
        # Нижняя граница
        stdscr.addstr(row, col, '+' + '-' * (max_len_names + 2) + 
                     '+-----------------+---------+--------------+')
        
        current_row = row + 2
    
    # Время
    minutes = int(total_time) // 60
    seconds = int(total_time) % 60
    time_str = f"Время с момента начала экзамена и до момента его завершения: {minutes}.{seconds:02d}"
    stdscr.addstr(current_row, 0, time_str)
    current_row += 2
    
    # Результаты
    stdscr.addstr(current_row, 0, f"Имена лучших студентов: {best_students}")
    current_row += 1
    stdscr.addstr(current_row, 0, f"Имена лучших экзаменаторов: {best_examiners}")
    current_row += 1
    stdscr.addstr(current_row, 0, f"Имена студентов, которых после экзамена отчислят: {expelled_students}")
    current_row += 1
    stdscr.addstr(current_row, 0, f"Лучшие вопросы: {best_questions}")
    current_row += 1
    stdscr.addstr(current_row, 0, f"Вывод: {conclusion}")
    
    stdscr.refresh()
    stdscr.getch()  # Ждем нажатия клавиши

def output_time(time_str):
    """Обновление только времени на экране"""
    global stdscr, last_time_row
    
    if 'stdscr' not in globals() or 'last_time_row' not in globals():
        return
    
    # Очищаем старую строку и пишем новую
    stdscr.addstr(last_time_row, 0, ' ' * 50)
    stdscr.addstr(last_time_row, 0, f"Время с момента начала экзамена: {time_str}")
    stdscr.refresh()

def display_updater(stdscr, students, examiners, student_queue, time_ptr, running_flag):
    while running_flag[0]:
        exam_output(students, examiners, time_ptr[0], student_queue)
        time.sleep(0.1)





def examiner_work(examiner: Examiner, student_queue, questions):
    # start_time = time.time()
    examiner.set_student(student_queue.get())
    while(examiner.get_student_name() != None):
        with threading.Lock():
            print(examiner.get_name(), ' ', examiner.get_student_name())
        time.sleep(3)
        with threading.Lock():
            print(examiner.get_name(), ' ', examiner.get_student_name(), 'сдал')
            examiner.set_student(student_queue.get())





def main():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)  # Скрыть курсор
    
    # Инициализация цветов
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Для сдавших
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Для проваливших
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Для информации

    examiners = read_persons("examiners.txt")
    students = read_persons("students.txt")
    questions = read_questions("questions.txt")

    t = [0]

    global stdscr_global, total_students_count, last_time_row
    stdscr_global = stdscr
    total_students_count = len(students)
    last_time_row = 4 + len(students) + len(examiners) * 2 + 5

    student_queue = queue.Queue()

    for student in students:
        student_queue.put(student)

    for _ in examiners:
        student_queue.put(None)

    running = [True]
    display_thread = threading.Thread(target=display_updater, args=(stdscr, students, examiners, student_queue, t, running))
    display_thread.start()

    threads = (threading.Thread(target = examiner_work, args = (ex, student_queue, questions)) for ex in examiners)
    # output_thread = threading.Thread(target = exam_output, args = (examiners, students, student_queue))
    
    # output_thread.start()
    for i in threads: i.start()

    for i in threads: i.join()
    # output_thread.join()
    running[0] = False
    display_thread.join()

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

    final_output(students, examiners, t[0], 
                 "Иван", "Степан, Михаил", "Варвара", 
                 "Там стоит стол, Человек собаке друг", "экзамен не удался")





stdscr = None
total_students_count = 0
last_time_row = 0

if __name__ == '__main__':
    main()