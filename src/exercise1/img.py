import curses
import prettytable
import asyncio
import requests
import os
from threading import Thread
import time
from pathlib import Path

table = prettytable.PrettyTable()
table.field_names = ["url", "status", "progress", "file"]

save_directory = ""
running = True

async def download(url, row_index):
    global save_directory
    try:
        # Обновляем статус на "Downloading"
        table.rows[row_index][1] = "Downloading"
        table.rows[row_index][2] = "0%"
        
        # Получаем имя файла из URL или генерируем
        filename = url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = f"image_{row_index}.jpg"
        
        # Полный путь для сохранения
        filepath = os.path.join(save_directory, filename)
        table.rows[row_index][3] = filename
        
        # Скачиваем файл с прогрессом
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Получаем размер файла
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        # Сохраняем файл
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        table.rows[row_index][2] = f"{progress}%"
        
        table.rows[row_index][1] = "Done"
        table.rows[row_index][2] = "100%"
    except Exception as e:
        table.rows[row_index][1] = "Error"
        table.rows[row_index][2] = "Failed"
        table.rows[row_index][3] = str(e)[:20]

def run_async_task(url, row_index):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download(url, row_index))
    loop.close()

def get_save_directory(screen: curses.window):
    screen.clear()
    screen.addstr("Enter save directory (will be created if doesn't exist):\n")
    screen.addstr("Press Enter for current directory\n> ")
    
    curses.echo()
    path = screen.getstr().decode('utf-8').strip()
    curses.noecho()
    
    if not path:
        path = os.getcwd()
    
    # Создаем директорию если не существует
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def main(screen):
    global save_directory, running
    
    # Настройка curses
    curses.curs_set(1)

    # Получаем директорию для сохранения
    save_directory = get_save_directory(screen)

    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    screen.nodelay(True)  # Неблокирующий ввод для автообновления


    
    s = ""
    last_update = time.time()
    update_interval = 0.1  # Обновление каждые 100мс
    
    while running:
        current_time = time.time()
        max_y, max_x = screen.getmaxyx()
        
        # Получаем ввод (неблокирующий)
        try:
            key = screen.getch()
        except:
            key = -1
        
        # Обработка ввода
        if key != -1:
            match key:
                case 127 | curses.KEY_BACKSPACE | 8:
                    if s:
                        s = s[:-1]
                case 10 | 13 | curses.KEY_ENTER:
                    if s.strip():
                        row_index = len(table.rows)
                        table.add_row([s, "Queued", "0%", ""])
                        
                        thread = Thread(target=run_async_task, args=(s, row_index))
                        thread.daemon = True
                        thread.start()
                        
                        s = ""
                case 27:  # ESC
                    running = False
                    break
                case _:
                    if 32 <= key <= 126:
                        if len(s) < max_x - 15:
                            s += chr(key)
        
        # Обновление экрана (с определенной частотой)
        if current_time - last_update >= update_interval:
            screen.erase()
            
            # Заголовок с информацией о директории
            header = f"Save directory: {save_directory}\n"
            header += "=" * min(len(header)-1, max_x-1) + "\n"
            screen.addstr(header)
            
            # Отображаем таблицу
            table_str = table.get_string()
            screen.addstr(table_str + "\n")
            
            # Отображаем текущий ввод
            prompt = "Enter URL (ESC to exit): "
            screen.addstr(prompt + s)
            
            # Обновляем позицию курсора
            table_lines = len(table_str.split('\n'))
            cursor_y = 2 + table_lines  # +2 для header
            cursor_x = len(prompt) + len(s)
            
            if cursor_y < max_y and cursor_x < max_x:
                screen.move(cursor_y, cursor_x)
            
            screen.refresh()
            last_update = current_time
        
        # Небольшая задержка для снижения нагрузки
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\nFiles saved to: {save_directory}")