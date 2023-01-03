# STM32 Timer Calculator - 2021
# Author: Orkun ZA

import numpy as np
import pandas as pd

import webbrowser

import tkinter as tk
import tkinter.scrolledtext as st

from tkinter import ttk
from tkinter import scrolledtext
from tkinter.font import BOLD
from tkinter import *

import atexit
import binascii
import os
import tempfile

from icon import iconhexdata
              
# Creating temp icon clean-up function.
def on_closing(iconfile):
    try:
        os.remove(iconfile.name)
    except Exception:
        pass

with tempfile.NamedTemporaryFile(delete=False) as iconfile:
    iconfile.write(binascii.a2b_hex(iconhexdata))

# Creating register a clean-up function.
atexit.register(lambda file=iconfile: on_closing(file))

# Creating function to display the link.
def callback(url):
    webbrowser.open_new_tab(url)

# Creating function to find solution
def findSolution(target__, clock__, tolerance__):
    TARGET_F = target__       # 1000  # In Hz so 50.0 is 0.020 seconds period and 0.25 is 4 seconds period
    CLOCK_MCU = clock__       # 84000000
    TOLERANCE = tolerance__   # 0.0001

    def abs_error(num1, num2):
        return abs((num1 - num2) / num1)

    def hertz(clock, prescaler, period):
        f = clock / (prescaler * period)
        return f

    def perfect_divisors():
        exacts = []
        for psc in range(1, 65536):
            arr = CLOCK_MCU / (TARGET_F * psc)
            if CLOCK_MCU % psc == 0:
                if arr <= 65536:
                    exacts.append(psc)
        return exacts

    def add_exact_period(prescaler):
        entries = []
        arr = CLOCK_MCU / (TARGET_F * prescaler)
        if arr == int(arr):
            entry = [prescaler, arr, TARGET_F, 0.0]
            entries.append(entry)
        return entries

    def possible_prescaler_value():
        possibles = []
        for psc in range(1, 65536):
            if psc in exact_prescalers:
                continue
            h1 = hertz(CLOCK_MCU, psc, 1)
            h2 = hertz(CLOCK_MCU, psc, 65536)
            if h1 >= TARGET_F >= h2:
                possibles.append(psc)
        return possibles

    def close_divisor(psc, tolerance):
        arr = CLOCK_MCU / (TARGET_F * psc)
        error = abs_error(int(arr), arr)
        if error < tolerance and arr < 65536.0:
            h = hertz(CLOCK_MCU, psc, int(arr))
            return psc, int(arr), h, error
        else:
            return None

    # Make a dataframe to hold results as we compute them
    df = pd.DataFrame(columns=['PSC', 'ARR', 'F', 'ERROR'], dtype=np.double)

    # Get exact prescalars first.
    exact_prescalers = perfect_divisors()
    exact_values = []
    for index in range(len(exact_prescalers)):
        rows = add_exact_period(exact_prescalers[index])
        for rowindex in range(len(rows)):
            df = df.append(pd.DataFrame(
                np.array(rows[rowindex]).reshape(1, 4), columns=df.columns))

    # Get possible prescalers.
    poss_prescalers = possible_prescaler_value()
    close_prescalers = []
    for index in range(len(poss_prescalers)):
        value = close_divisor(poss_prescalers[index], TOLERANCE)
        if value is not None:
            close_prescalers.append((value[0], value[1], value[2], value[3]))
    df = df.append(pd.DataFrame(np.array(close_prescalers).reshape(
        len(close_prescalers), 4), columns=df.columns))

    #  Adjust PSC and ARR values by -1 to reflect the way you'd code them.
    df['PSC'] = df['PSC'] - 1
    df['ARR'] = df['ARR'] - 1

    #  Sort first by errors (zeroes and lowest errors at top of list, and
    #  then by prescaler value (ascending).
    df = df.sort_values(['ERROR', 'PSC'])

    # Make and populate column indicating if combination is exact.
    df['EXACT'] = pd.Series("?", index=df.index)
    df['EXACT'] = np.where(df['ERROR'] == 0.0, "YES", "NO")

    #  Format for output.
    df['PSC'] = df['PSC'].map('{:.0f}'.format)
    df['ARR'] = df['ARR'].map('{:.0f}'.format)
    df['F'] = df['F'].map('{:.6f}'.format)
    df['ERROR'] = df['ERROR'].map('{:.10f}'.format)

    output = df.to_string()
    print(output)
    print()
    print('these are the ',
          df.shape[0], ' total combination meeting your tolerance requirement')

    return output

# Creating function to button operation
def button_command():
    temp_Target = TARGET_combobox.get()
    temp_Clock = MCU_combobox.get()

    if (temp_Target == "Hz"):
        transform_Target = int(TARGET_F_input.get())
    elif (temp_Target == "kHz"):
        transform_Target = int(TARGET_F_input.get())*1000
    elif (temp_Target == "MHz"):
        transform_Target = int(CLOCK_MCU_input.get())*1000000

    if (temp_Clock == "Hz"):
        transform_Clock = int(CLOCK_MCU_input.get())
    elif(temp_Clock == "kHz"):
        transform_Clock = int(CLOCK_MCU_input.get())*1000
    elif (temp_Clock == "MHz"):
        transform_Clock = int(CLOCK_MCU_input.get())*1000000

    send_Target = transform_Target
    send_Clock = transform_Clock
    send_Tolerance = float(TOLERANCE_input.get())

    result = findSolution(send_Target, send_Clock, send_Tolerance)

    text_area.configure(state='normal')
    text_area.delete('0.0', END)
    text_area.insert(END, result)
    text_area.configure(state='disabled')

    return None

# Creating function to centering popup window
def center_window(width=300, height=200):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

# ----------------------------------------------- Tkinter starts here ----------------------------------------------- #


# Creating Class for Tkinter
root = Tk()
root.title("STM32 Timer Calculator")
center_window(400, 620)
# root.geometry("400x700")
root.resizable(width=False, height=False)
root.iconbitmap(iconfile.name)

# Creating Label to display the header #002052
Label_Header = Label(root, text="STM32 Timer Calculator",
                     font=("TkDefaultFont", 10),
                     fg='white',
                     background='#002052',
                     padx=115)
Label_Header.pack(pady=1)

# __________________________________________________________________________________________________Target Freq__INPUT__
# Creating Label to display the Target Frequency
Label_FREQ = Label(root, text="Target Frequency",
                   font=("TkDefaultFont", 10),
                   background='#32aede',
                   fg='white',
                   padx=134)
Label_FREQ.pack(pady=5)

# Creating Entry to get Target Frequency
TARGET_F_input = Entry(root, width=25)
TARGET_F_input.insert(END, "10")
TARGET_F_input.pack()

# Creating Combobox for Select the Target Frequency Conversion Factor
string_TARGET = tk.StringVar()
TARGET_combobox = ttk.Combobox(root, state="readonly",
                               textvariable=string_TARGET,
                               values=["Hz", "kHz", "MHz"],
                               width=22)
TARGET_combobox.current(1)
TARGET_combobox.pack(pady=5)

# _____________________________________________________________________________________________________MCU Freq__INPUT__
# Creating Label to display the MCU Clock Frequency
Label_CLOCK = Label(root, text="MCU Clock Frequency",
                    font=("TkDefaultFont", 10),
                    background='#32aede',
                    fg='white',
                    padx=119)
Label_CLOCK.pack(pady=5)

# Creating Entry to get MCU Clock Frequency
CLOCK_MCU_input = Entry(root, width=25)
CLOCK_MCU_input.insert(END, "72")
CLOCK_MCU_input.pack()

# Creating Combobox for Select the MCU Clock Frequency Conversion Factor
string_MCU = tk.StringVar()
MCU_combobox = ttk.Combobox(root, state="readonly",
                            textvariable=string_MCU,
                            values=["Hz", "kHz", "MHz"],
                            width=22)
MCU_combobox.current(2)
MCU_combobox.pack(pady=5)

# ____________________________________________________________________________________________________TOLERANCE__INPUT__
# Creating Label to display the Calculation Tolerance
Label_TOLERANCE = Label(root, text="Calculation Tolerance",
                        font=("TkDefaultFont", 10),
                        background='#32aede',
                        fg='white',
                        padx=122)
Label_TOLERANCE.pack(pady=5)

# Creating Entry to get Calculation Tolerance
TOLERANCE_input = Entry(root, width=25)
TOLERANCE_input.insert(END, "0.0001")
TOLERANCE_input.pack()

# Creating Button to Start Calculation #525152
StartButton = Button(root, text="Calculate",
                     command=button_command,
                     height=1,
                     font=("TkDefaultFont", 10),
                     background='#525152',
                     fg='white',
                     padx=154)
StartButton.pack(pady=10)

# Creating Label to display the Results Header
Label_Results = Label(root, text="Calculation Results",
                      font=("TkDefaultFont", 10),
                      background='#32aede',
                      height=1,
                      fg='white',
                      padx=128)
Label_Results.pack(pady=2)

# Creating Scrolled text to display the Results
text_area = st.ScrolledText(root, width=50, height=19, font=("consolas", 10))
text_area.insert(tk.INSERT, """ Waiting for calculation...""")
text_area.pack()

# Creating Label to display the link
link = Label(root, text="GitHub@orkunza",
             font=('consolas', 8), fg="grey", cursor="hand2")
link.pack(pady=4)
link.bind("<Button-1>", lambda e:
          callback("https://github.com/orkunza"))

root.mainloop()
# ------------------------------------------------ Tkinter ends here ------------------------------------------------ #

# cd VScode\PythonWorkspace
# pyinstaller.exe --onefile --icon=-image.ico --windowed timerClac.py

# C:\Users\X571\VScode\PythonWorkspace
