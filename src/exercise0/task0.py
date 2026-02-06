import random

class Students:
    name: str
    gender: str
    state: str = 'Очередь'

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    pass

class Examiners:
    name: str
    gender: str
    state: str = '-'
    number_of_students: int = 0
    failed_students: int = 0
    work_time: int = 0

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    def sentiment(self) -> int:
        return random.randint(-1, 1)



def queue_input(filename: str) -> list:
    persons = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip()
            if line and len(parts) == 2:
                persons.append(Students(parts[0], parts[1]) if filename == 'students.txt' else Examiners(parts[0], parts[1]))
    return persons


