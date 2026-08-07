"""---------------------------------------------------------------------------------------
 Module: decorator

 Author = Roberta Fischetti

 Date = 2026-07-28

 Description = decorator - assignment: 
    a) Create a decorator in decorator.py
 
    0. CONNECT the decorator "print_process" with all sleeping functions.
    Print START and END before and after.
       
        START *******
        main_function
        END *********

    1. Print the processing time of all sleeping functions.
        
        END - 00:00:00

    2. PRINT the name of the sleeping function in the decorator.
        How can you get the information inside it?

        START - long_sleeping
---------------------------------------------------------------------------------------"""

import time
from datetime import datetime

# DECORATOR -------------------------------------------------------------
def print_process(func):
    def wrapper(*args):
        start = datetime.now()
        print(f"START: {func.__name__}") 
        func(args)                      
        end = datetime.now()
        print(f"END: {end.strftime("%H:%M:%S.%f")}")  
        print(f"processing time: {end - start}.")
    return wrapper


# FUNCTIONS -------------------------------------------------------------
@print_process
def short_sleeping(name):
    time.sleep(.1)
    print(name)

@print_process
def mid_sleeping(name):
    time.sleep(2)
    print(name)

@print_process
def long_sleeping(name):
    time.sleep(4)
    print(name)


# START -------------------------------------------------------------
short_sleeping("so sleepy")
mid_sleeping("so sleepy")
long_sleeping("so sleepy")
