#!/usr/bin/env python
'''
ACDSee photo sorter.
Script is searching for opened in ADCSee image file and copying it by pressing Enter. 
'''
import argparse
import shlex
import textwrap
import os
import pathlib
import shutil
# from threading import settrace
import win32gui
import ctypes
import keyboard
import notifications


__author__ = 'Dmitriy Sidov'
__version__ = '0.4.1'
__maintainer__ = 'Dmitriy Sidov'
__email__ = 'dmitriy.sidov@gmail.com'
__status__ = 'With argparse'


# System defaults init here
def _parse_args(arguments=None):
    parser = argparse.ArgumentParser(
        description=textwrap.dedent('''
        HOW TO USE
        ----------
        Put .exe file into photos root folder and run program.
        Enter search file extension.
        (It will search for all files with specified extension inside this folder except /_sorted/ folder)
        Start ACDSee, switch files and press 'x' when you see matching photo.
        You will see success message if file was copied and error message if something gone wrong.

        !Warning! You will not be able to copy the new photo until the message disappears!

        Files copy into /_sorted/ folder. Files in this folder are not indexing for copy.

        COMMANDS
        --------
        # usage (by console): program.exe [option] 
        usage (by .exe): type [option]
        '''), 
        formatter_class=argparse.RawTextHelpFormatter,                                        
        epilog=textwrap.dedent(f'''
        examples:
            -e jpg
            -a -i D:\\Users\\User\\Pictures -k c

        MISC
        ----
        For correct functioning, filename extensions must be enabled.
        To do it: go Windows Explorer -> View -> File name extension.


        AUTHOR/RELEASES
        ---------------
        Dmitriy Sidov
        https://github.com/dsidov/acdsee-sorter
        v{__version__} - 2021'''),
        add_help=False)

    # parser.add_argument('-a','--any', action='store_true', help='search file in any active window, not only ACDSee')
    parser.add_argument('-e','--extension', default='.NEF', type=str, help='file extension')
    # parser.add_argument('-g','--gui', action='store_false', help='don\'t show GUI interface')       
    parser.add_argument('-h','--help', action='store_true', help='show this help message')
    parser.add_argument('-i','--input', default='.', type=str, action='store', help='input directory path')
    parser.add_argument('-k','--key', default='x', type=str, action='store', help='change default key')
    parser.add_argument('-o','--output', default='./_sorted', type=str, action='store', help='output directory path')
    # parser.add_argument('-s', '--superficial', action='store_true', help='search filename only in active window')
    parser.add_argument('-t', '--title', default='ACDSee', type=str, action='store', help='search for specified title in active window')
    
    if (arguments is None) or (arguments == ''):
        args = parser.parse_args()
    else:
        args = parser.parse_args(shlex.split(arguments))
    
    # rm when add GUI    
    if args.help:
        parser.print_help()
    return args

# add output folder files checking - done!
# if file_path.startswith(abs output path) - done!
def get_filepaths(folder_path, file_extension, copy_path):
    folder_path_abs = os.path.abspath(folder_path).replace('\\','/') + '/'
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


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW(f'ACDSee sorter v{__version__}')
    
    print('--- ACDSee images sorter ---')
     
    # if no files found repeat
    while True:
        input_data = input('\nEnter command (-h to get help) or press Enter to continue.\n> ')
        settings = _parse_args(input_data)
        print(settings)
        if settings.help:
            
            continue
        
        settings.extension = settings.extension.lower()
        if not settings.extension.startswith('.'):
            settings.extension = '.' + settings.extension
    
        print('Indexing files...', end=' ')

        file_paths, file_names, sorted_names = get_filepaths(settings.input, settings.extension, settings.output)
        print('Done.')
        
        if len(file_paths) == 0: 
            print(f'-------\nERROR! 0 files found. Check file extension & .exe folder.')
        else:
            print(f'-------\n{len(file_paths)} {settings.extension} files found.', end=' ')
            
            # checking is only 1 acdsee process running    
            titles = get_titles(settings.title, None)
            if len(titles) > 1:
                print('WARNING! Several ACDSee copies are running! Please leave only one.')
            elif len(titles) == 0:
                print('WARNING! ACDSee is not running! Start the wiever')
            break

    if len(sorted_names) > 0:
        sorted_last = sorted(list(sorted_names))[-1]
        print(f'{len(sorted_names)} file(s) already sorted. Last sorted file is {sorted_last}.')
    if len(file_paths) != len(file_names):
        print('WARNING! Several files with same name exist! Only 1 file will be copied!')

    print(f'---\nPress {settings.key} if you see matching photo. Press CTRL+C to exit.')
    
    notification = notifications.Notifications()
    
    while True:
        try:
            keyboard.wait(settings.key)
            
            has_error = True
            title = get_active_title(settings.title, settings.extension)
            if len(title) == 0:
                titles = get_titles(settings.title, settings.extension)
                if len(titles) > 1:
                    notification.msg_error_proc(text='ERROR! Several ACDSee copies are running.') # Please close unused.')
                    print('ERROR! Several ACDSee copies are running. Please close unused.')
                elif len(titles) == 0:
                    notification.msg_error_proc(text='ERROR! Start ACDSee and choose the file.')
                    print('ERROR! Start ACDSee and choose the file.')
                elif titles[0] not in file_names:
                    notification.msg_error_proc(text='ERROR! File not found! Choose file in viewer.')
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
                            notification.msg_error_proc(text='ERROR! File already exist!')
                        else:
                            print(f'{title} is copying...', end=' ')
                            was_copied = copy_file(path, settings.output)
                            if was_copied is True:
                                sorted_names.add(sorted_new)
                                notification.msg_success_proc(text=f'{sorted_new} saved. Sorted {len(sorted_names)}')
                                print(f'Done. Sorted: {len(sorted_names)}. Progress: {round(100*i/len(file_paths))}%')                                
                                break
                            else:
                                notification.msg_error_proc(text='ERROR!')
                                print('Error!')
        except KeyboardInterrupt:
            print('\nProgram is stopping...')
            break