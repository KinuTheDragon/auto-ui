from os.path import basename
import re

def to_app(data):
    commands_filename = data["filenames"]["commands"]
    icon_filename = data["filenames"]["icon"]
    content_data = data["content"]
    
    NUM_PAGES = max(content_data["page titles"].keys()) + 1
    
    with open(commands_filename) as f:
        commands = f.read()
    
    setup = f"""
from tkinter import *

{commands}

class HideableWidget:
    __widgets = []
    
    def __init__(self, widget, page, grid_params):
        self.widget = widget
        self.page = page
        self.grid_params = grid_params
        self.__class__.__widgets.append(self)
    
    @classmethod
    def update(cls):
        for widget in cls.__widgets:
            if current_screen == widget.page:
                widget.widget.grid(**widget.grid_params)

screen = Tk()

screen.geometry("500x500")
screen.title("{content_data["overall title"]}")
screen.iconbitmap("{basename(icon_filename)}")
screen.resizable(False, False)

blank = PhotoImage("blank.png")

Label(screen, text = "{content_data["overall title"]}", image = blank, compound = "top", bg = "#cccccc", width = 500, height = 50).grid(row = 0, column = 0, columnspan = 2)

heading_label = Label(screen, text = "{content_data["page titles"].get(0, "")}", image = blank, compound = "top", bg = "#00ffff", width = 500, height = 50)
heading_label.grid(row = 1, column = 0, columnspan = 2)

widget_frame = Frame(screen, width = 500, height = 335)
widget_frame.grid(row = 2, column = 0, columnspan = 2)
widget_frame.grid_propagate(False)

current_screen = 0

def prev_command():
    global current_screen
    current_screen -= 1
    next_button.config(state = NORMAL)
    if current_screen == 0:
        prev_button.config(state = DISABLED)
    heading_label.config(text = {content_data["page titles"]}.get(current_screen, ""))
    HideableWidget.update()

def next_command():
    global current_screen
    current_screen += 1
    prev_button.config(state = NORMAL)
    if current_screen == {NUM_PAGES} - 1:
        next_button.config(state = DISABLED)
    heading_label.config(text = {content_data["page titles"]}.get(current_screen, ""))
    HideableWidget.update()

prev_button = Button(screen, text = "< Prev", image = blank, compound = "top", width = 250, height = 50, command = prev_command)
prev_button.grid(row = 3, column = 0)
prev_button.config(state = DISABLED)

next_button = Button(screen, text = "Next >", image = blank, compound = "top", width = 250, height = 50, command = next_command)
next_button.grid(row = 3, column = 1)
if {NUM_PAGES} == 1:
    next_button.config(state = DISABLED)
""".strip()
    
    var_codes = []
    for variable, value in content_data["variables"].items():
        if variable.startswith("$"): var_type = "StringVar"
        elif variable.startswith("%"): var_type = "IntVar"
        name = variable[1:]
        var_code = f"{name} = {var_type}(value = {repr(value)})"
        var_codes.append(var_code)
    
    codes = []
    for thing in content_data["widgets and startfuncs"]:
        if thing["type"] == "widget":
            widget_code = "{name} = HideableWidget({type}(widget_frame, **{json}), {pos[0]}, {{'row': {pos[1]}, 'column': {pos[2]}, 'sticky': W}}).widget".format(**thing["object"])
            widget_code = re.compile("['\"][$%&]([^'\"]+)['\"]").sub(r"\1", widget_code)
            codes.append(widget_code)
        else:
            codes.append(thing["object"] + "()")
    
    output = "\n\n".join([
        setup,
        "\n".join(var_codes),
        "\n\n".join(codes),
        "HideableWidget.update()"
    ])
    
    return output