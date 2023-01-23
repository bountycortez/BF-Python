import tkinter as tk
import asyncio
import subprocess
import threading

# Create the main window
root = tk.Tk()
root.title("Async Command Launcher")

class app():

    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(100, 100)

        self.start_button1 = tk.Button(self.root, text="start", command=lambda: self.create_await_funct(self.start_button1,self.testfield1))
        self.start_button1.pack()

        self.testfield1 = tk.Label(self.root, text="output")
        self.testfield1.pack()

        self.start_button2 = tk.Button(self.root, text="start", command=lambda: self.create_await_funct(self.start_button2,self.testfield2))
        self.start_button2.pack()

        self.testfield2 = tk.Label(self.root, text="output")
        self.testfield2.pack()
        self.root.mainloop()

    def create_await_funct(self,button,testfield):
        threading.Thread(target=lambda loop: loop.run_until_complete(self.await_funct(button,testfield)),
                         args=(asyncio.new_event_loop(),)).start()
        button["relief"] = "sunken"
        button["state"] = "disabled"

    async def await_funct(self,button,testfield):
        testfield["text"] = "start waiting"
        self.root.update_idletasks()

        await asyncio.sleep(2)

        testfield["text"] = "end waiting"
        self.root.update_idletasks()

        await asyncio.sleep(2)

        testfield["text"] = "output"
        self.root.update_idletasks()
        button["relief"] = "raised"
        button["state"] = "normal"


if __name__ == '__main__':
    app()