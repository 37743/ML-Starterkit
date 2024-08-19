''' 
This module contains a decorator that creates a new thread
 with a process using the input function
'''

from threading import Thread

def thread(function):
    ''' 
    Creates a new thread with a process using the input function
    '''
    def wrap(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return wrap