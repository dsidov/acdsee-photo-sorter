#!/usr/bin/env python
'''
ACDSee photo sorter.

Script is searching for opened in ADCSee image file and copying it by pressing Enter. 
File name extension option should be on!
'''


import os
import pathlib
import shutil
import time
import win32gui


__author__ = 'Dmitriy Sidov'
__version__ = '0.1.1'
__maintainer__ = 'Dmitriy Sidov'
__email__ = 'dmitriy.sidov@gmail.com'
__status__ = 'Is it working?'


FOLDER_PATH = '.'
COPY_PATH = './_sorted'
DEFAULT_EXTENSION = '.NEF'
DEFAULT_TITLE = 'ACDSee'


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


def get_title(search_title : str, file_extension):

    search_title = search_title.lower()

    def EnumHandler(hwnd, titles): 
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if search_title in title.lower():
                titles.append(title)
    
    raw_titles = list()    
    win32gui.EnumWindows(EnumHandler, raw_titles)

    titles = list()

    for title in raw_titles:
        if file_extension.lower() in title.lower(): # when windows explorer shows file extensions
            title_formatted = title[:title.find(file_extension)] + file_extension
            if len(title_formatted) > len(file_extension):
                titles.append(title_formatted)
    return titles


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


print('ACDSee images sorter')

while True:
    input_ext = input('Enter file extension (def is .NEF). Type -h to get help.')
    if '-h' in input_ext:
        print(f'''
        Usage:
        Put .exe file into photos root folder and run program.
        Start ACDSee, use wheel to change photos and press enter when you see matching photo.
        
        File name extensions should be on!
        (Windows Explorer -> View -> File name extension)
        
        Author/releases:
        https://github.com/dsidov/acdsee-photo-sorter
        
        Version {__version__} 
        ''')
    elif input_ext == '':
        input_ext = DEFAULT_EXTENSION
    else:
        input_ext = input_ext.lower()
        if not input_ext.startswith(FOLDER_PATH):
            input_ext = '.' +  input_ext
    print('Indexing files...', end=' ')

    file_paths, file_names, sorted_names = get_filepaths(FOLDER_PATH, input_ext, COPY_PATH)
    print('Done')
    
    if len(file_paths) == 0: 
        print(f'-------\n0 files found. Check file extension & .exe folder.', end=' ')
    else:
        print(f'-------\n{len(file_paths)} {input_ext} files found.', end=' ')
        break


if len(sorted_names) > 0:
    sorted_last = sorted(list(sorted_names))[-1]
    print(f'{len(sorted_names)} file(s) already sorted. Last sorted file is {sorted_last}.')
if len(file_paths) != len(file_names):
    print('WARNING! Several files with same name exist! Only 1 file will be copied!')

# print(file_paths, file_names)
print('---\nPress Enter if you see matching photo.')


while True:
    not_enter = input()
    if not_enter != '':
        break
    else:
        titles = get_title(DEFAULT_TITLE, input_ext)
        if len(titles) > 1:
            print('WARNING! Several ACDSee copies are running. Please close unused.')
        elif len(titles) == 0:
            print('WARNING! Start ACDSee and choose the file.')
        elif titles[0] not in file_names:
            print('WARNING! File not Found. Put program in root folder and restart the program.')
        else:
            i = 0
            for path in file_paths:
                i += 1
                if path.lower().endswith(titles[0].lower()):
                    sorted_new = os.path.basename(path)
                    if sorted_new in sorted_names:
                        print(f'{sorted_new} is already exist!')
                    else:
                        print(f'{titles[0]}. Copying...', end=' ')
                        time_st = time.time()
                        was_copied = copy_file(path, COPY_PATH)
                        if was_copied is True:
                            time_end = time.time()
                            sorted_names.add(sorted_new)
                            print(f'Sorted: {len(sorted_names)}. Progress: {round(100*i/len(file_paths))}%. Done.')
                            # Time: {round(time_end - time_st,3)}.
                            break
                        else:
                            print('Error!')