#!/usr/bin/env python
'''
ACDSee photo sorter.

Script is searching for opened in ADCSee image file and copying it by pressing Enter. 
File name extension option should be on!
'''


import os
import pathlib
import shutil
import win32gui
import ctypes
import keyboard
import notifications


__author__ = 'Dmitriy Sidov'
__version__ = '0.3.2'
__maintainer__ = 'Dmitriy Sidov'
__email__ = 'dmitriy.sidov@gmail.com'
__status__ = 'Keypress version only'


FOLDER_PATH = '.'
COPY_PATH = './_sorted'
DEFAULT_EXTENSION = '.NEF'
DEFAULT_TITLE = 'ACDSee'
DEFAULT_KEY = 'x' # def key/shortcut for file copying

def get_filepaths(folder_path, file_extension, copy_path):

    folder_path_abs = os.path.abspath(folder_path)
    copy_path_abs = os.path.abspath(copy_path).replace('\\','/') + '/'
    if not os.path.exists(folder_path_abs):
        print(f'ERROR: {__name__}.get_filepaths. Рath {folder_path} doesn\'t exist.')
        return None, None, None
    else:
        file_paths = list()
        file_names = set()
        sorted_names = set()
        f_extension = file_extension.lower()

        for folder, _, files in os.walk(folder_path_abs):
            for f in files:
                if f_extension in f.lower():
                    folder_path = folder.replace('\\','/') + '/'
                    if folder_path == copy_path_abs:
                        sorted_names.add(f)
                    else:
                        file_paths.append(folder_path + f)
                        file_names.add(f)
    return file_paths, file_names, sorted_names


def get_titles(search_title : str, file_extension):

    search_title = search_title.lower()

    def EnumHandler(hwnd, titles): 
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if search_title in title.lower():
                titles.append(title)
    
    raw_titles = list()    
    win32gui.EnumWindows(EnumHandler, raw_titles)
    
    if file_extension is not None:
        titles = list()
        for title in raw_titles:
            if file_extension.lower() in title.lower(): # when windows explorer shows file extensions
                title_formatted = title[:title.find(file_extension)] + file_extension
                if len(title_formatted) > len(file_extension):
                    titles.append(title_formatted)
        return titles
    else:
        return raw_titles


def get_active_title(search_title, file_extension):
    search_title = search_title.lower()
    raw_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    if file_extension.lower() in raw_title.lower():
        title_formatted = raw_title[:raw_title.find(file_extension)] + file_extension
        if len(title_formatted) > len(file_extension):
            return title_formatted
    return ''


def copy_file(file_path, copy_path):
    
    file_name = os.path.split(file_path)[-1]
    new_dir = os.path.abspath(copy_path).replace('\\','/')
    
    if not new_dir.endswith('/'):
        new_dir += '/' 
    new_path = new_dir + file_name
   
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    shutil.copyfile(file_path, new_path)
    
    if os.path.isfile(new_path) and (pathlib.Path(file_path).stat().st_size == pathlib.Path(new_path).stat().st_size):
        return True
    else:
        return False


# def notify_user(is_error=False, box_title='Title', box_message='Message'):
#     if is_error:
#         winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
#         ctypes.windll.user32.MessageBoxW(0, box_message, box_title, 0)
#     else:
#         ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
        
        
if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW(f'ACDSee sorter v{__version__}')
    
    print('ACDSee images sorter')
    
    titles = get_titles(DEFAULT_TITLE, None)
    if len(titles) > 1:
        print('WARNING! Several ACDSee copies are running! Please leave only one.')
    elif len(titles) == 0:
        print('WARNING! ACDSee is not running! Start the wiever')

    while True:
        input_ext = input('Enter file extension (def is .NEF). Type -h to get help. ')
        if '-h' in input_ext:
            print(f'''
            Usage:
            Put .exe file into photos root folder and run program.
            Start ACDSee, use wheel to change photos and press enter when you see matching photo.
            
            File name extensions should be on!
            (Windows Explorer -> View -> File name extension)
            
            Author/releases:
            https://github.com/dsidov/acdsee-sorter
            
            Version {__version__} 
            ''')
            continue
        elif input_ext == '':
            input_ext = DEFAULT_EXTENSION
        else:
            input_ext = input_ext.lower()
            if not input_ext.startswith(FOLDER_PATH):
                input_ext = '.' +  input_ext
        print('Indexing files...', end=' ')

        file_paths, file_names, sorted_names = get_filepaths(FOLDER_PATH, input_ext, COPY_PATH)
        print('Done.')
        
        if len(file_paths) == 0: 
            print(f'-------\nERROR! 0 files found. Check file extension & .exe folder.')
        else:
            print(f'-------\n{len(file_paths)} {input_ext} files found.', end=' ')
            break

    if len(sorted_names) > 0:
        sorted_last = sorted(list(sorted_names))[-1]
        print(f'{len(sorted_names)} file(s) already sorted. Last sorted file is {sorted_last}.')
    if len(file_paths) != len(file_names):
        print('WARNING! Several files with same name exist! Only 1 file will be copied!')

    print(f'---\nPress {DEFAULT_KEY} if you see matching photo. Press CTRL+C to exit.')
    
    notification = notifications.Notifications()
    
    while True:
        try:
            keyboard.wait(DEFAULT_KEY)
            
            has_error = True
            title = get_active_title(DEFAULT_TITLE, input_ext)
            if len(title) == 0:
                titles = get_titles(DEFAULT_TITLE, input_ext)
                if len(titles) > 1:
                    notification.msg_error(text='ERROR! Several ACDSee copies are running.') # Please close unused.')
                    print('ERROR! Several ACDSee copies are running. Please close unused.')
                elif len(titles) == 0:
                    notification.msg_error(text='ERROR! Start ACDSee and choose the file.')
                    print('ERROR! Start ACDSee and choose the file.')
                elif titles[0] not in file_names:
                    notification.msg_error(text='ERROR! File not found! Choose file in viewer.')
                    print('ERROR! File not found! Choose file in viewer.')
                else:
                    title = titles[0]
                    has_error = False
            else:
                has_error = False    
                
            if not has_error:
                i = 0
                for path in file_paths:
                    i += 1
                    if path.lower().endswith(title.lower()):
                        sorted_new = os.path.basename(path)
                        if sorted_new in sorted_names:
                            print(f'ERROR! {sorted_new} already exists!')
                            notification.msg_error(text='ERROR! File already exist!')
                        else:
                            print(f'{title} is copying...', end=' ')
                            was_copied = copy_file(path, COPY_PATH)
                            if was_copied is True:
                                sorted_names.add(sorted_new)
                                notification.msg_success(text=f'{sorted_new} saved. Sorted {len(sorted_names)}')
                                print(f'Done. Sorted: {len(sorted_names)}. Progress: {round(100*i/len(file_paths))}%')                                
                                break
                            else:
                                notification.msg_error(text='ERROR!')
                                print('Error!')
        except KeyboardInterrupt:
            print('\nProgram is stopping...')
            break