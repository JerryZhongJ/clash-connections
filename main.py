# !/usr/bin/env python

import time
from readchar import readkey, key
import requests
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich import box
import os
from threading import Lock, Thread


RESTFUL_PORT = 9090
AUTH_USER = None
AUTH_PASS = None



import time
from rich.live import Live
from rich.table import Table



def synchronized(func):
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)
    return wrapper


class Clash:
    def __init__(self):
        self._lock = Lock()
        self._selected_row = 0
        self._selected_id = None
        self.update()

    @property
    @synchronized
    def connections_selected(self):
        return self._connections, self._selected_row
    
    def _get_id(self, row):
        return self._connections[row]["id"] if len(self._connections) > row else None
    
    @synchronized
    def update(self):
        r = requests.get(f'http://localhost:{RESTFUL_PORT}/connections', auth=(AUTH_USER, AUTH_PASS) if AUTH_USER else None) 
        if(r.status_code != 200):
            exit()
        
        result = r.json()
        self._connections = result["connections"]
        self._connections.sort(key=lambda connection:connection["start"])

        for connection in self._connections:
            if connection["id"] == self._selected_id or self._selected_id == None:
                self._selected_row = self._connections.index(connection)
                self._selected_id = self._get_id(self._selected_row)
                break
        else:
            self._selected_row = min(len(self._connections) - 1, self._selected_row)
            self._selected_id = self._get_id(self._selected_row)

    @synchronized
    def select_prev(self):
        self._selected_row = max(0, self._selected_row - 1)
        self._selected_id = self._get_id(self._selected_row)

    @synchronized
    def select_next(self):
        self._selected_row = min(len(self._connections) - 1, self._selected_row + 1)
        self._selected_id = self._connections[self._selected_row]["id"]

    

def get_table(clash) -> Table:
    table = Table(box=box.SIMPLE,)
    table.width = os.get_terminal_size().columns
    table.add_column("PROCESS", style="sandy_brown", ratio=1)
    table.add_column("DESTINATION", style="light_goldenrod2", ratio=3)
    table.add_column("RULE", style="dark_sea_green2", ratio=1)
    table.add_column("PROXY", style="pale_turquoise1", ratio=3)
    table.add_column("UPLOAD", style="sky_blue1", ratio=1)
    table.add_column("DOWNLOAD", style="sky_blue2", ratio=1)
    connections, selected_row = clash.connections_selected
    for i in range(0, len(connections)):
        connection = connections[i]
        table.add_row(
            connection["metadata"]["processPath"].split("/")[-1],
            connection["metadata"]["host"],
            connection["rule"],
            connection["chains"][0],
            str(connection["upload"]),
            str(connection["download"]),
            style="on red" if i == selected_row else None
        )

    return table

class KeyListener(Thread):
    def __init__(self, clash):
        super().__init__()
        self.clash = clash
    def run(self):
        print("listerner started")
        while True:
            k = readkey()
            print(k)
            if k == key.UP:
                
                clash.select_prev()
            elif k == key.DOWN:
                
                clash.select_next()


if __name__ == "__main__":

    clash = Clash()
    listener = KeyListener(clash)
    listener.start()
    # listener = keyboard.Listener(on_press=on_press)
    # listener.start()
    # listener.wait()

    try:
        with Live(None, refresh_per_second=100, screen=True) as live:  # update 4 times a second to feel fluid
            lasttime = time.time()
            while(True):
                curtime = time.time()
                if curtime - lasttime > 0.5:
                    clash.update()
                live.update(get_table(clash))
                time.sleep(0.01)
    except KeyboardInterrupt:
        pass