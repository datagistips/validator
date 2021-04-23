import tkinter as tk
from tkinter import ttk

tkwindow = tk.Tk()

cbox = ttk.Combobox(tkwindow, values=[1,2,3], state='readonly')
cbox.grid(column=0, row=0)

def callback(eventObject):
    print(eventObject)
    print(cbox.current(), cbox.get())

    # We get the source column and the target column

    # We get the type of the target column

    # We check if source column is ok

    # If ok, color combobox item in green, else red

cbox.bind("<<ComboboxSelected>>", callback)

tkwindow.mainloop()