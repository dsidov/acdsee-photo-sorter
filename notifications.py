#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter
import ctypes
import winsound
import win32gui

# def active_window_get():
#     title = win32gui.GetForegroundWindow()
#     return title

# def active_window_set(title):
#     win32gui.SetForegroundWindow(title)

class Notifications():
    BORDER_COEFF = 2.6
    def __init__(self, font_size=18, offset=[25,25], max_lenght=40, has_taskbar=True, colors=['#fff','#ff0000'], 
                 alpha=.8, display_time=[1,3]):
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
            colors : list of color's HEX
            alpha : float (0...1)
            display_time : list of ints
                Window destroy delay
        '''
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics
        metrics = ctypes.windll.user32.GetSystemMetrics
        if has_taskbar:
            self.display = [metrics(16), metrics(17)]
        else:
            self.display = [metrics(0), metrics(1)]
         
        self.exist = False
         
        self.font_size = font_size 
        self.offset = offset
        # 1.34 - pt to px coeff, 0.6 - width to height coeff for monospace fonts 
        self.font_dimensions = [round(font_size * 1.34 * .604) , round(font_size * 1.34)] 
        self.max_length = max_lenght
        
        for color in colors:
            if not color.startswith('#'): # doesn't work!!!
                color = '#' + color
        self.color = colors
        self.alpha = alpha
        self.display_time = display_time
            
    
    def msg_success(self, text: str, active_window=None): # do I need active window? 
        if len(text) > self.max_length:
            text = text[:self.max_length]
        width = round(self.font_dimensions[0] * len(text) + self.BORDER_COEFF)
        height = round(self.font_dimensions[1] * self.BORDER_COEFF)
    
        self.notification = tkinter.Tk()
        self.notification['bg'] = self.color[0] 
        self.notification.wm_attributes('-alpha',self.alpha)
        self.notification.overrideredirect(True)
        self.notification.attributes("-topmost", True)
        # todo - add frame around message

        self.notification.geometry(f'{width}x{height}+{self.display[0]-width-self.offset[0]}+{self.display[1]-height-self.offset[1]}')
        self.notification.resizable(width=False, height=False)
        label = tkinter.Label(self.notification, text=text, font=f'Consolas {self.font_size} bold', bg=self.color[0], bd=0)
        label.place(relx=.5, rely=.5, anchor='center')
        
        # self.notification.bind('<x>', lambda _: self.notification.destroy())
        self.notification.bind('<Button-1>', lambda _: self.notification.destroy())
        self.notification.after(self.display_time[0]*1000, lambda: self.notification.destroy())
        # if active_window is not None:
            # active_window_set(active_window)
        
        self.notification.mainloop()
        
        
    def msg_error(self, text: str, extended_errors=False):
        '''
        Creates error message.
        
        Parameters
        ----------
        text : str
        extended errors : boolean.
                If True show blink & play sound at error message
        '''
        if len(text) > self.max_length:
            text = text[:self.max_length]
        width = round(self.font_dimensions[0] * (len(text) + self.BORDER_COEFF))
        height = round(self.font_dimensions[1] * self.BORDER_COEFF)
        
        self.notification=tkinter.Tk()   
        self.notification['bg'] = self.color[1]
        self.notification.wm_attributes('-alpha',self.alpha)
        self.notification.overrideredirect(True)
        self.notification.attributes("-topmost", True)
                
        self.notification.geometry(f'{width}x{height}+{self.display[0]-width-self.offset[0]}+{self.display[1]-height-self.offset[1]}')
        self.notification.resizable(width=False, height=False)
        label = tkinter.Label(self.notification, text=text, font=f'Consolas {self.font_size} bold', bg=self.color[1])
        label.place(relx=.5, rely=.5, anchor='center')

        self.notification.bind('<x>', lambda _: self.notification.destroy())
        self.notification.bind('<Button-1>', lambda _: self.notification.destroy())        
        self.notification.after(self.display_time[1]*1000, lambda: self.notification.destroy())
        
        if extended_errors:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
        self.notification.mainloop()