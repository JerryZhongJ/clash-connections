import sys
import termios
import builtins
from threading import Thread
import atexit

def initTerminal():
    fd = sys.stdin.fileno() 
    old_settings = termios.tcgetattr(fd)

    atexit.register(termios.tcsetattr, fd, termios.TCSANOW, old_settings)

    term = termios.tcgetattr(fd)
    try:
        term[3] &= ~(termios.ICANON | termios.ECHO | termios.IGNBRK)
        termios.tcsetattr(fd, termios.TCSANOW, term)
    except: 
        exit()

    
    

UP = "\x1b\x5b\x41"
DOWN = "\x1b\x5b\x42"
DELETE = "\x1b\x5b\x33\x7e"

# This fuction is copied from https://github.com/magmax/python-readchar.git/
# Thanks to [magmax](https://github.com/magmax)
def readkey() -> str:
    """Get a keypress. If an escaped key is pressed, the full sequence is
    read and returned as noted in `_posix_key.py`."""

    c1 = sys.stdin.read(1)

    if c1 in "\x03":
        exit()
    
    if c1 != "\x1B":
        return c1

    c2 = sys.stdin.read(1)
    if c2 not in "\x4F\x5B":
        return c1 + c2

    c3 = sys.stdin.read(1)
    if c3 not in "\x31\x32\x33\x35\x36":
        return c1 + c2 + c3

    c4 = sys.stdin.read(1)
    if c4 not in "\x30\x31\x33\x34\x35\x37\x38\x39":
        return c1 + c2 + c3 + c4

    c5 = sys.stdin.read(1)
    return c1 + c2 + c3 + c4 + c5

class KeyListener(Thread):
    def __init__(self, clash):
        initTerminal()
        
        super().__init__()
        self.clash = clash
        self.daemon = True
    def run(self):
        while True:
            key = readkey()
            if key == UP:  
                self.clash.select_prev()
            
            elif key == DOWN:
                self.clash.select_next()
              
            elif key == DELETE:
                self.clash.stopConnection()
             