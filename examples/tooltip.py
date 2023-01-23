import tkinter
import customtkinter
from idlelib.tooltip import Hovertip
import pprint


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

#app = customtkinter.CTk()
app = tkinter.Tk()
app.geometry("400x240")
#app.configure(fg_color="black",bg_color="red",bg="red")

def button_function():
    print("button pressed")

#button = customtkinter.CTkButton(master=app, text="Button with Tootip", command=button_function)
button = tkinter.Button(master=app, text="Button with Tootip", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

buttonquittip=Hovertip(button,"""
    
    i'm the button tooltip!
    another line

    """)
#buttonquittip.tipwindow.
#buttonquittip=Hovertip(button,'Hello World!')

print(buttonquittip.text)
pprint.pprint(buttonquittip.__dict__)

app.mainloop()