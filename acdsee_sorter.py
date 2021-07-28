#!/usr/bin/env python
'''
ACDSee photo sorter.
Script is searching for opened in ADCSee image file and copying it by pressing Enter. 
'''
import argparse
import multiprocessing
import shlex
import textwrap
import os
import pathlib
import shutil
# from threading import settrace
import win32gui
import ctypes
import keyboard
# ↓ custom
import notifications
# import 

# https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
multiprocessing.freeze_support() 


__author__ = 'Dmitriy Sidov'
__version__ = '0.4.4'
__maintainer__ = 'Dmitriy Sidov'
__email__ = 'dmitriy.sidov@gmail.com'
__status__ = 'Refactored to classes'


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
    parser.add_argument('-b','--brute', action='store_true', help='Search files from input folder in ANY software (may work slow)')
    parser.add_argument('-e','--extension', default='.NEF', type=str, help='file extension')
    # parser.add_argument('-g','--gui', action='store_false', help='don\'t show GUI interface')       
    parser.add_argument('-h','--help', action='store_true', help='show this help message')
    parser.add_argument('-i','--input', default='.', type=str, action='store', help='input directory path')
    parser.add_argument('-k','--key', default='x', type=str, action='store', help='change default key')
    parser.add_argument('-o','--output', default='./_sorted', type=str, action='store', help='output directory path')
    # parser.add_argument('-s', '--superficial', action='store_true', help='search filename only in active window')
    parser.add_argument('-t', '--title', default=' - ACDSee', type=str, action='store', help='search for specified title in active window')
    
    if (arguments is None) or (arguments == ''):
        args = parser.parse_args()
    else:
        args = parser.parse_args(shlex.split(arguments)) # remove when gui?
    
    # rm when add GUI (?)
    if args.help:
        parser.print_help()
    return args


class Sorter:
    
    def _get_files_and_paths(self, path_input, path_output, extension, verbose):
        if verbose:
            print('Indexing files...', end=' ')
        path_input_abs = os.path.abspath(path_input).replace('\\','/') + '/'
        path_output_abs = os.path.abspath(path_output).replace('\\','/') + '/'
        
        if not os.path.exists(path_input_abs):
            print(f'ERROR: {__name__}.get_filepaths. Рath {path_input} doesn\'t exist.')
            self.path_input = None
        else:
            self.path_input = path_input_abs
            self.path_output = path_output_abs
            
            if not os.path.exists(path_output_abs):
                os.makedirs(path_output)
            
            self.files = list()
            self.filenames = set()
            self.filenames_sorted = set()
            self.extension = extension.lower()

            for folder, _, files in os.walk(self.path_input):
                for f in files:
                    if f.lower().endswith(self.extension):
                        folder_path = folder.replace('\\','/') + '/'
                        if folder_path == self.path_output:
                            self.filenames_sorted.add(f)
                        else:
                            self.files.append(folder_path + f)
                            self.filenames.add(f)
            
            if verbose:
                print('Done.')
                
            if len(self.files) == 0: 
                print(f'-------\nERROR! 0 files found. Check file extension & .exe folder.')
            elif verbose:
                print(f'-------\n{len(self.files)} {self.extension} files found.', end=' ')

            if verbose:
                if len(self.filenames_sorted) > 0:
                    sorted_last = sorted(list(self.filenames_sorted))[-1]
                    print(f'{len(self.filenames_sorted)} file(s) already sorted. Last sorted file is {sorted_last}.')
                if len(self.filenames) != len(self.files):
                    print('WARNING! Several files with same name exist! Only 1 file will be copied!')


    def __init__(self, path_input, path_output, extension, title, brute_search=False, verbose=True): # TODO add brute
        if verbose:
            ctypes.windll.kernel32.SetConsoleTitleW(f'ACDSee sorter v{__version__}')
        self._get_files_and_paths(path_input, path_output, extension, verbose)
        self.title = title
        
        # checking what title do we have to save time
        titles = self._get_titles()
        if len(titles) > 1:
            print('WARNING! Several ACDSee copies are running!')
        elif len(titles) == 0:
            print('WARNING! ACDSee is not running! Start the wiever')


    def _get_active_filename(self):
        raw_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if self.extension in raw_title.lower():
            title_formatted = raw_title[:raw_title.find(self.title)]
            if len(title_formatted) > len(self.extension):
                return title_formatted
        else: 
            return None


    def _get_titles(self):

        def EnumHandler(hwnd, titles): 
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.title in title.lower():
                    titles.append(title)
        
        raw_titles = list()    
        win32gui.EnumWindows(EnumHandler, raw_titles)
        
        if self.extension is not None:
            titles = list()
            for title in raw_titles:
                if self.extension in title.lower(): # when windows explorer shows file extensions
                    title_formatted = title[:title.find(self.title)]
                    if len(title_formatted) > len(self.extension):
                        titles.append(title_formatted)
            return titles
        else:
            return raw_titles


    def copy_active_file(self, notification=notifications.Notification()):
        '''
        Searches a file name in the active title, checks does it have path in self.files, tries to copy.
        '''
        active_filename = self._get_active_filename()
        if active_filename is None:
            notification.msg_error_proc(text='ERROR! File not found! Choose file in viewer.')
        else:
            i = 0
            for file in self.files:
                i += 1
                if file.endswith(active_filename):
                    sorted_new = os.path.basename(file)
                    if active_filename in self.filenames_sorted:
                        print(f'ERROR! {sorted_new} already exists!')
                        notification.msg_error_proc(text='ERROR! File already exist!')
                    else:
                        print(f'{file} is copying...', end=' ')
                        new_path = self.path_output + sorted_new
                        shutil.copyfile(file, new_path)
                        if os.path.isfile(new_path) and (pathlib.Path(file).stat().st_size == pathlib.Path(new_path).stat().st_size):
                            self.filenames_sorted.add(sorted_new)
                            notification.msg_success_proc(text=f'{sorted_new} saved. Sorted {len(self.filenames_sorted)}')
                            print(f'Done. Sorted: {len(self.filenames_sorted)}. Progress: {round(100*i/len(self.files))}%')
                        else:
                            notification.msg_error_proc(text='''ERROR! Can't copy file''')
                            print('''ERROR! Can't copy file''')
                            

if __name__ == "__main__":

    while True:
        input_data = input('\nEnter command (-h to get help) or press Enter to continue.\n> ')
        settings = _parse_args(input_data)
        print(settings)
        if settings.help:
            continue
        
        settings.extension = settings.extension.lower()
        if not settings.extension.startswith('.'):
            settings.extension = '.' + settings.extension
        break

    sorter = Sorter(settings.input, settings.output, settings.extension, settings.title)
    
    while True:
        try:
            keyboard.wait(settings.key)
            sorter.copy_active_file()
        except KeyboardInterrupt:
            print('\nProgram is stopping...')
            break