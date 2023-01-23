import tkinter
import customtkinter
import pprint


class Textbox(tkinter.Frame):

    def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        super().__init__()

        # ensure a consistent GUI size
        self.grid_propagate(True)

        # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # create a Text widget
        #bgcolor=self.master["fg_color"]
        bgcolor=self.master["bg"]
        fgcolor='#DCE4EE'
        #pprint.pprint(self.__dict__)
        #pprint.pprint(self.master.__dict__)
        self.txt = tkinter.Text(self)
        #pprint(self.txt.__dict__)
        self.txt.configure(bg=bgcolor,fg=fgcolor)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        

        # create a Scrollbar and associate it with txt
        scrollb = tkinter.Scrollbar(self, command=self.txt.yview, activebackground=bgcolor,bg='red')
        pprint.pprint(scrollb.__dict__)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set

    def configureTextbox(self, *args, **kwarg):
        self.txt.configure(*args, **kwarg)

    def insert(self, *args, **kwarg):
        self.txt.insert(*args, **kwarg)

    def see(self, *args, **kwarg):
        self.txt.see(*args, **kwarg)

    def configure(self,*args, **kwarg):
        self.txt.configure(*args, **kwarg)




customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

root=customtkinter.CTk()

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)

#textbox = customtkinter.CTkTextbox(root, spacing1=0, spacing2=0, spacing3=5) 
#textbox = tkinter.Text(root, spacing1=0, spacing2=0, spacing3=5) 
textbox = Textbox(root) 
textbox.configureTextbox(spacing1=0, spacing2=0, spacing3=5)

textbox.grid(row=0, column=0, rowspan=4, padx=(20, 20), pady=(20, 20), sticky="nsew")
for i in range(1,8000): 
    textbox.insert("end", 
        """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n""" 
    * 1)
textbox.configure(state="disabled")
textbox.see("end")

progressbar = customtkinter.CTkProgressBar(root)
progressbar.grid(row=0, column=1, padx=20, pady=10)
progressbar.configure(mode="indeterminate")
progressbar.start()

root.mainloop()
