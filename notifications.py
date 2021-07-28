#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter
import ctypes
import winsound
import multiprocessing


class Notification():
    BORDER_COEFF = 2.6
    def __init__(self, font_size=18, offset=[25,25], max_lenght=60, has_taskbar=True, colors=['fff','ee3e34'], 
                font_colors=['000', 'fff'], border_size=2, border_colors=['000','fff'], alpha=.9, display_time=[2,4]):
        '''
        Creates Notification object for further displaying.
        
        Parameters
        ----------
            font_size : int, default 18
                Message text size.
            offset : list of ints
                Message window offset from bottom-right side (x,y).
            max_length : int
                Max length of text message.
            has_taskbar : boolean
                If True calculate offset with taskbar size.
            colors : list of str
                HEXes of background colors.
            font_colors : list of str
                HEXes of font colors.
            border_size : int
                Border size in pixels.
            border_colors : list of str
                HEXes of corder colors.
            alpha : float (0...1)
            display_time : list of ints
                Window destroy delay is seconds.
        '''
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics
        metrics = ctypes.windll.user32.GetSystemMetrics
        if has_taskbar:
            self.display = [metrics(16), metrics(17)]
        else:
            self.display = [metrics(0), metrics(1)]
         
        self.font_size = font_size 
        self.offset = offset
        # 1.34 - pt to px coeff, 0.6 - width to height coeff for monospace fonts 
        self.font_dimensions = [round(font_size * 1.34 * .604) , round(font_size * 1.34)] 
        self.max_length = max_lenght
        
        for color_list in [colors, font_colors, border_colors]:
            for i in range(2):
                if not color_list[i].startswith('#'): # doesn't work!!!
                    color_list[i] = '#' + color_list[i]
        
        self.colors = colors
        self.font_colors = font_colors
        self.border_size = border_size
        self.border_colors = border_colors
        self.alpha = alpha
        self.display_time = display_time
    
    
    def _msg_init(self, type, text): # type 0 - success, type 1 - error
        if len(text) > self.max_length:
            text = text[:self.max_length]
            
        width = round(self.font_dimensions[0] * len(text) + self.BORDER_COEFF)
        height = round(self.font_dimensions[1] * self.BORDER_COEFF)
        
        self.notification = tkinter.Tk()
        self.notification['bg'] = self.border_colors[type] 
        self.notification.wm_attributes('-alpha',self.alpha)        
        self.notification.overrideredirect(True)
        self.notification.attributes("-topmost", True)                
        
        self.notification.geometry(f'{width}x{height}+{self.display[0]-width-self.offset[0]}+{self.display[1]-height-self.offset[1]}')
        self.notification.resizable(width=False, height=False)
    
        frame = tkinter.Frame(self.notification, width=width-2*self.border_size, height=height-2*self.border_size,
                              bg=self.colors[type])
        frame.place(x=self.border_size, y = self.border_size)
        label = tkinter.Label(self.notification, text=text, font=f'Consolas {self.font_size} bold', 
                              bg=self.colors[type], fg=self.font_colors[type], bd=0)
        label.place(relx=.5, rely=.5, anchor='center')        
        
        self.notification.after(self.display_time[type]*1000, lambda: self.notification.destroy())        

            
    def _msg_terminate(self):
        if hasattr(self,'process') and self.process.is_alive():
            self.process.terminate()        


    def msg_success(self, text: str):
        '''
        Creates a message that file has been copied. Block copying till message exist.
        Dissapears over time. Can be closed by mouse click.
        '''
        self._msg_init(0, text)
        
        # self.notification.bind('<x>', lambda _: self.notification.destroy())
        self.notification.bind('<Button-1>', lambda _: self.notification.destroy())
        self.notification.after(self.display_time[0]*1000, lambda: self.notification.destroy())
        
        self.notification.mainloop()
        
        
    def msg_success_proc(self, text: str):
        '''
        Creates a message that file has been added (copied).
        Process that terminate itself when a new message come.
        Dissapears over time. Can be closed by mouse click.
        '''
        self._msg_terminate()        
        self.process = multiprocessing.Process(target=self.msg_success, args=(text,))
        self.process.start()
        
        
    def msg_error(self, text: str, extended_errors=False):
        '''
        Creates a message that error was encountered. Block copying till message exist.
        Dissapears over time. Can be closed by mouse click.
        
        Parameters
        ----------
        text : str
        extended_errors : boolean
            Adds Windows error sound & flash program icon.
        '''
        self._msg_init(1, text)

        # self.notification.bind('<x>', lambda _: self.notification.destroy())
        self.notification.bind('<Button-1>', lambda _: self.notification.destroy())        
        
        self.notification.mainloop()
        
        if extended_errors:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)


    def msg_error_proc(self, text: str, extended_error=False):
        '''
        Creates a message that error was encountered.
        Process that terminate itself when a new message come.
        Dissapears over time. Can be closed by mouse click.
        
        Parameters
        ----------
        text : str
        extended_errors : boolean
            Adds Windows error sound & flash program icon.        
        '''
        self._msg_terminate()
        self.process = multiprocessing.Process(target=self.msg_error, args=(text,extended_error,))
        self.process.start()