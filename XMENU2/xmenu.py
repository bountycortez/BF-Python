# ==========================================================================================================================
# xmenu by BF
# --------------------------------------------------------------------------------------------------------------------------
# 20230408 BF V0.1 birth of app
# ==========================================================================================================================
import os
import sys
import argparse
import logging
import configparser
import time
import datetime
import json

###@import tkinter
###@import idlelib
###@from idlelib.tooltip import Hovertip
###@import customtkinter

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
#from ttkbootstrap.scrolled import ScrolledText

import threading
import queue
import functools
import subprocess

#import pprint
import inspect



#---------------------------------------------------------------------------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------------------------------------------------------------------------
PRGNAME = 'XMENU'
PRGDESCRIPTION='''
A Command Menu Programm
'''
PRGEPILOG='''
'''

LOGFORMAT = PRGNAME+' %(asctime)s Thread [%(threadName)s] %(thread)d %(levelname)s: %(message)s'
LOGMODE = "w"

RETVAL_OK=(0, "OK")
RETVAL_JSON_PARSE_ERROR=(10, "JSON-PARSE-ERROR")
RETVAL_NO_MENUITEMS_ERROR=(10, "NO-MENUITEMS-ERROR")
RETVAL_SESSIONLOGFILE_OPEN_ERROR=(10, "SESSION-LOGFILE-OPEN-ERROR")

GUI_MINWIDTH=600
GUI_MINHEIGHT=400
GUI_REFRESH_FAST = 50 # milliseconds
GUI_REFRESH_SLOW = 500 # milliseconds
GUI_MAXQUEUESIZE = 5000
GUI_MAXQUEUEITEMS = 3
GUI_MAXLINEBUFFER = 3000 # maximum tkinter survives on my mac
GUI_CLEARLINES = 1000


###@# customtkinter theme
###@# Modes: "System" (standard), "Dark", "Light"
###@customtkinter.set_appearance_mode("System")
###@# Themes: "blue" (standard), "green", "dark-blue"
###@customtkinter.set_default_color_theme("blue")


#---------------------------------------------------------------------------------------------------------------------------
# BASIC APP CLASS
#---------------------------------------------------------------------------------------------------------------------------
class App():
    """The Basic App Class with logging and command line options"""

    # define initialize
    def __init__(self):

        # return value
        self.retval=RETVAL_OK

        # system encoding
        self.encoding=sys.getdefaultencoding()

        # app cconfig/ini filename
        self.inifilename = os.path.join(os.path.expanduser("~"),"."+PRGNAME)
        
        # command line parsing and setup logging
        self.parser = argparse.ArgumentParser(
            description=PRGDESCRIPTION,
            epilog=PRGEPILOG+'''
            bye.
            '''
            )

        # setup arguments
        self.setup_arguments()

        # parse all options 
        self.options = self.parser.parse_args()

        # get logging directory
        self.logdir = self.options.logdir

        # get loglevel
        self.loglevels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warn': logging.WARNING,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        self.loglevel = self.loglevels.get(self.options.log.lower())
        if self.loglevel is None:
            raise ValueError(
                f"log level given: {self.options.log}"
                f" -- must be one of: {' | '.join(self.loglevels.keys())}")

        # setup logging
        self.logfilename=os.path.join(os.path.expanduser(self.logdir),PRGNAME.lower()+".log")
        logging.basicConfig(level=self.loglevel,
                            format=LOGFORMAT,
                            encoding=self.encoding,
                            handlers=[
                                logging.FileHandler(self.logfilename,LOGMODE),
                                logging.StreamHandler()
                            ])
        self.logger = logging.getLogger(__name__)

        # log start timestamp, current dir and encoding
        self.logger.info(f"Starting {PRGNAME} (logfile={self.logfilename},encoding={self.encoding})...")
        self.logger.info(f"Current directory: {os.getcwd()}")
        self.logger.info(f"Current encoding: {self.encoding}")

        # log options found
        for option in vars(self.options):
            self.logger.info(f"Found Option {option}: {getattr(self.options,option)}")

        # read the settings from ~/.<PRGNAME>
        self.read_settings()

        # analyze app command line arguments
        self.analyze_arguments()


    # define cleanup
    def cleanup(self):
        self.write_settings()
        if self.retval>RETVAL_OK:
            self.logger.critical(f"Failed {PRGNAME} (retval={self.retval})!")
        else:
            self.logger.info(f"Done {PRGNAME} (retval={self.retval})!")
        return


    # define command line arguments (detail in child class)
    def setup_arguments(self) -> bool:
        """
        EXAMPLE:
        #argument --test
        self.parser.add_argument(
            "-test", 
            "--test", 
            action='store_true',
            help=(
                "Provide Testing option "
                "Example --test, default='False'"),
        )
        """
        
        # log level option
        self.parser.add_argument(
            "-log", 
            "--log", 
            default="info",
            help=(
                "Provide logging level. "
                "Example --log debug, default='INFO'"),
        )

        # logdir option
        self.parser.add_argument(
            "-logdir", 
            "--logdir", 
            default=".",
            help=(
                "Provide logging directory. "
                "Example --logdir ./log, default='.'"),
        )

        return True


    #parse command line arguments (detail in child class)
    def analyze_arguments(self) -> bool:
        
        # logdir already set earlier
        self.logger.info(f"LOGDIR set to: {self.logdir}")

        """
        EXAMPLE:
        # argument --test
        self.testing = self.options.test
        self.logger.info(f"TEST set to: {self.testing}")
        """

        return True


    # save settings in inifile (detail in child class)
    def write_settings(self) -> bool:

        try:
            with open(self.inifilename, 'w', encoding=self.encoding) as inifile:
                self.appconfig.write(inifile)
        except:
            self.logger.warning(f"save_settings(): Cannot write app config file {self.inifilename}!")
            return False

        return True


    # read settings from inifile (detail in child class)
    def read_settings(self) -> bool:

        self.logger.info(f"Inifilename: {self.inifilename}")
        self.appconfig = configparser.ConfigParser()

        foundfiles = self.appconfig.read(self.inifilename, encoding=self.encoding)
        if not foundfiles:
            self.logger.info(f"Have not found app config file {self.inifilename}, creating one ...")
            self.write_settings()
            foundfiles = self.appconfig.read(self.inifilename, encoding=self.encoding)
            if not foundfiles:
                self.logger.warning(f"Warning: Have not found and cannot write app config file {self.inifilename}!")
                return False

        return True




#---------------------------------------------------------------------------------------------------------------------------
# BASIC GUI APP CLASS
#---------------------------------------------------------------------------------------------------------------------------
class GuiApp(App,ttk.Window):
    """The Basic tttkbootsrap GUI App Class"""

    # extend the class initialization
    def __init__(self):

        ttk.Window.__init__(self,themename="darkly")
        ###@customtkinter.CTk.__init__(self)

        # get the current screen width and height
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.win_width = int(self.screen_width / 3)
        self.win_height = int(2 * self.screen_height / 3)
        self.win_x = self.win_width
        self.win_y = int(self.win_height-self.win_height/2)

        # after geometry is defined (otherwise read_settings does not work correctly)
        App.__init__(self)

        # log the screen size
        self.logger.info(f"Screen width: {self.screen_width}")
        self.logger.info(f"Screen height:{self.screen_height}")
        self.logger.info(f"Window Width: {self.win_width}")
        self.logger.info(f"Window Height: {self.win_height}")
        self.logger.info(f"Window X: {self.win_x}")
        self.logger.info(f"Window Y: {self.win_y}")

        # configure main window
        self.title(PRGNAME)
        self.win_geometry = f'{self.win_width}x{self.win_height}+{self.win_x}+{self.win_y}'
        self.logger.debug(f"Window Geometry: {self.win_geometry}")
        self.geometry(self.win_geometry)

        # initialize session logfile
        self.sessionlogfilename=os.path.join(os.path.expanduser(self.logdir),PRGNAME.lower()+"-session.log")
        try:
            self.sessionlogfile=open(file=self.sessionlogfilename,mode="w",encoding=self.encoding)
            self.logger.info(f"Session logfile is {self.sessionlogfilename}...")
            timestampstring=datetime.datetime.now().strftime("%Y%m%d %H:%m:%S")
            msg=PRGNAME+': '+timestampstring+' STARTING...'+'\n'
            self.sessionlogfile.write(msg)

        except Exception as err:
            self.logger.error(f"While opening session logfile {self.sessionlogfilename}: Unexpected {err=}, {type(err)=}")
            self.retval=RETVAL_SESSIONLOGFILE_OPEN_ERROR
            self.destroy()
            return

    # extend destroy
    def destroy(self):
        try:
            timestampstring=datetime.datetime.now().strftime("%Y%m%d %H:%m:%S")
            msg=PRGNAME+': '+timestampstring+' BYE.'+'\n'
            self.sessionlogfile.write(msg)
            self.sessionlogfile.close()
            self.logger.info(f"Closed session logfile {self.sessionlogfilename}.")
        except:
            pass

        App.cleanup(self)
        
        ###@customtkinter.CTk.destroy(self)
        ttk.Window.destroy(self)


    # extend define app arguments here
    def setup_arguments(self) -> bool:

        App.setup_arguments(self)

        ## option --test
        ##self.parser.add_argument(
        ##    "-test", 
        ##    "--test", 
        ##    action='store_true',
        ##    help=(
        ##        "Provide Testing option "
        ##        "Example --test, default='False'"),
        ##)

        return True


    # extend parse app arguments here
    def analyze_arguments(self) -> bool:

        App.analyze_arguments(self)

        ### argument --test
        ##self.testing = self.options.test
        ##self.logger.info(f"TEST set to: {self.testing}")

        return True


    # read settings from inifile (detail in child class)
    def read_settings(self) -> bool:

        retval=App.read_settings(self)
        #if retval == False:
        #    return retval
    
        # set found settings
        try:
            self.win_x=int(self.appconfig["WINDOW"]["x"])
            if self.win_x > self.screen_width:
                self.win_x=int(self.screen_width / 3)
        except:
            pass

        try:
            self.win_y=int(self.appconfig["WINDOW"]["y"])
            if self.win_y > self.screen_height:
                self.win_y=int(self.win_height-self.win_height/2)
        except:
            pass

        try:
            self.win_width=int(self.appconfig["WINDOW"]["width"])
            if (self.win_width>self.screen_width):
                self.win_width=int(self.screen_width)
        except:
            pass

        try:
            self.win_height=int(self.appconfig["WINDOW"]["height"])
            if (self.win_height>self.screen_height):
                self.win_height=int(self.screen_height)
        except:
            pass

        return retval


    # save settings in inifile (detail in child class)
    def write_settings(self) -> bool:

        self.appconfig["WINDOW"]={}
        x=self.winfo_x()
        self.appconfig["WINDOW"]["x"] = f'{x}'
        y=self.winfo_y()
        self.appconfig["WINDOW"]["y"] = f'{y}'
        width=self.winfo_width()
        self.appconfig["WINDOW"]["width"] = f'{width}'
        height=self.winfo_height()
        self.appconfig["WINDOW"]["height"] = f'{height}'

        retval=App.write_settings(self)

        return retval


    # for chanching appearance
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ###@customtkinter.set_appearance_mode(new_appearance_mode)
        self.logger.info(f"Appearance set to {new_appearance_mode}...")


    # for changing scaling
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        
        ###@customtkinter.set_widget_scaling(new_scaling_float)
        ###self.tk.call('tk','scaling',new_scaling_float)
        ##self.call('tk','scaling',2.0)
        self.logger.info(f"Scaling set to {new_scaling}...")


    # for clearing the textbox
    def clear_textbox(self):
        ###@self.textbox.configure(state="normal")
        self.textbox.configure(state="normal")
        self.textbox.delete('1.0','end')
        ###@self.textbox.configure(state="disabled")
        self.textbox.configure(state="disabled")


    # setup main window
    def setup_mainwindow(self, cols, rows):

        # configure main window grid layout (cols x rows)
        if cols<3:
            cols=3
        if rows<10:
            rows=10

        self.minsize(GUI_MINWIDTH,GUI_MINHEIGHT)

        #main control column    
        self.grid_columnconfigure((0,cols-1), weight=0, minsize=200)

        #textbox column
        self.grid_columnconfigure(1, weight=3, minsize=300)
        
        row=0
        while row < rows:
            self.grid_rowconfigure(row, weight=1)
            row+=1
        #self.grid_rowconfigure((0,1,2,3,4), weight=1)
            
        # create apperance and scaling choice
        ###@self.utils_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent") # , fg_color='red'
        self.utils_frame = ttk.Frame(self) # , fg_color='red' , fg_color="transparent"
        self.utils_frame.grid(row=0, column=0, rowspan=rows, sticky="nsew")
        self.utils_frame.grid_columnconfigure(0, weight=0)

        ###@self.appearance_mode_label = customtkinter.CTkLabel(self.utils_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label = ttk.Label(self.utils_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=1, column=4, padx=20, pady=(10, 0))
        ###@self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.utils_frame, values=["System","Light", "Dark"],command=self.change_appearance_mode_event)
        self.appearance_var = tk.StringVar(self)
        self.appearance_var.set("System")
        self.apperance_lst=["System","System","Light", "Dark"]
        self.appearance_mode_optionemenu = ttk.OptionMenu(self.utils_frame,self.appearance_var,*self.apperance_lst,command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=2, column=4, padx=20, pady=(10, 10))
        ###@self.appearance_mode_optionemenu.set("System")
        ###@self.change_appearance_mode_event(self.appearance_mode_optionemenu._current_value)

        ###@self.scaling_label = customtkinter.CTkLabel(self.utils_frame, text="UI Scaling:", anchor="w")
        self.scaling_label = ttk.Label(self.utils_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=3, column=4, padx=20, pady=(10, 0))
        ###@self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.utils_frame, values=["80%", "90%", "100%", "110%", "120%"],command=self.change_scaling_event)
        self.scaling_var = tk.StringVar(self)
        self.scaling_var.set("100%")
        self.scaling_lst=["100%","80%", "90%", "100%", "110%", "120%"]
        self.scaling_optionemenu = ttk.OptionMenu(self.utils_frame,self.scaling_var,*self.scaling_lst,command=self.change_scaling_event)
        ##self.scaling_optionemenu = ttk.Combobox(self.utils_frame,textvariable=self.scaling_var,values=self.scaling_lst)
        ##self.scaling_optionemenu.bind('<<ComboboxSelected>>',self.change_scaling_event)
        ## self.scaling_var.set("100%")
        self.scaling_optionemenu.grid(row=4, column=4, padx=20, pady=(10, 20))
        ###@self.scaling_optionemenu.set("100%")
        ###@self.change_scaling_event(self.scaling_optionemenu._current_value)

        # create debug enable, clear and quit button
        ###@self.dbgcheckbox = customtkinter.CTkCheckBox(master=self.utils_frame, text="Debug Logging")
        self.debug_var = tk.IntVar(self)
        self.debug_var=0
        self.dbgcheckbox = ttk.Checkbutton(master=self.utils_frame, text="Debug Logging", variable=self.debug_var, bootstyle="success,round-toggle")
        self.dbgcheckbox.grid(row=5, column=4, pady=10, padx=20, sticky="n")
        ###@self.dbgcheckboxtip=idlelib.tooltip.Hovertip(self.dbgcheckbox,"""
        self.dbgcheckboxtip=ToolTip(self.dbgcheckbox,text="""for enabling debug logging if not started in debugging mode""",bootstyle="light, inverse")
        if self.loglevel==logging.DEBUG:
            self.dbgcheckbox.select()
            self.dbgcheckbox.configure(state="disabled")

        # there is still a problem with tootip in system auto dark mode, text is not visible
        #pprint.pprint(self.dbgcheckboxtip.anchor_widget.__dict__)

        # create clear button
        ###@self.clearbutton = customtkinter.CTkButton(self.utils_frame, text="Clear Output", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.clearbutton = ttk.Button(self.utils_frame, text="Clear Output")
        self.clearbutton.configure(command=self.clear_textbox)
        self.clearbutton.grid(row=7, column=4, padx=20, pady=(10, 10), sticky="nsew")

        # create quit button
        ###@self.quitbutton = customtkinter.CTkButton(self.utils_frame, text="Quit", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.quitbutton = ttk.Button(self.utils_frame, text="Quit")
        self.quitbutton.configure(command=self.destroy)
        self.quitbutton.grid(row=8, column=4, padx=20, pady=(10, 10), sticky="nsew")

        # create textbox
        ###@self.textbox_frame = customtkinter.CTkFrame(self, width=500, corner_radius=0) #, fg_color='green'
        self.textbox_frame = ttk.Frame(self, width=500) #, fg_color='green'
        self.textbox_frame.grid(row=0, column=1, rowspan=rows, sticky="nsew")
        self.textbox_frame.grid_rowconfigure(0, weight=4)
        self.textbox_frame.grid_columnconfigure(0, weight=4) # minsize=300

        ###@self.textbox = customtkinter.CTkTextbox(self.textbox_frame, spacing1=0, spacing2=0, spacing3=5) # , fg_color="blue"
        self.textbox = ttk.ScrolledText(self.textbox_frame, spacing1=0, spacing2=0, spacing3=5) # , fg_color="blue"
        self.textbox.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.textbox.configure(state="disabled")



#---------------------------------------------------------------------------------------------------------------------------
# FINAL APP CLASS
#---------------------------------------------------------------------------------------------------------------------------
class XmenuApp(GuiApp):
    """The Final XMENU App for starting commands via GUI buttons"""

    # the class initialization
    def __init__(self):

        super().__init__()

        # initialize lists
        self.menuitems=[]
        self.cmdnames=[]
        self.cmdoutputs=[]

        self.cmdbuttons=[]
        self.cmdprogressbars=[]
        self.cmdthreads=[]
        self.cmdretvals=dict()
        self.cmdqueues=[]

        # load commands
        self.load_commands()

        # initialize the mainwindow
        self.setup_mainwindow(cols=3,rows=len(self.menuitems))

        # setup command column in the gui
        self.setup_commands()

        #create the threading lock and install the queue check
        self.check_queues()

        return


    # extend destroy
    def destroy(self):

        self.logger.info(f"Shutting down (current thread count: {threading.active_count()})...")
        # waiting for threads to end
        for thread in self.cmdthreads:
            threadid=thread.ident
            threadnativeid=thread.native_id
            self.logger.info(f"Waiting for thread {thread.name} (ident={threadid}/nativeid={threadnativeid}) to shut down (is alive: {thread.is_alive()})")
            thread.join()
        
        # get thread retvals
        for thread in self.cmdthreads:
            threadid=thread.ident
            threadnativeid=thread.native_id
            retval=self.cmdretvals[threadid]
            self.logger.info(f"Thread {thread.name} (ident={threadid}/nativeid={threadnativeid}) result: {retval}")

        while True:
            if self.process_queues()==0:
                break
        
        # wait till the queued work has been done
        self.logger.info(f"Waiting for work in queues to be done...")
        for queue in self.cmdqueues:
            queue.join()

        return super().destroy()


   # extend define app arguments here
    def setup_arguments(self) -> bool:

        super().setup_arguments()

        ### argument --xxx
        ##self.parser.add_argument(
        ##    "-xxx", 
        ##    "--xxx", 
        ##    action='store_true',
        ##    help=(
        ##        "Provide Testing option "
        ##        "Example --xxx, default='False'"),
        ##)        

        # argument cmdfile dir
        self.parser.add_argument(
            "-cmdfiledir", 
            "--cmdfiledir", 
            default=".",
            help=(
                "Provide json commandfile directory. "
                "Example --cmdfiledir ./cfg, default='.'"),
        )

        return True


    # extend parse app arguments here
    def analyze_arguments(self) -> bool:

        super().analyze_arguments()

        ### argument --xxx
        ##self.xxx = "xxx"
        ##self.logger.info(f"XXX set to: {self.xxx}")

        # get cmdfiledir directory
        self.cmdfiledir=self.options.cmdfiledir
        self.logger.info(f"CMDFILEDIR set to: {self.cmdfiledir}")

        return True

    def setup_commands(self):

        # create first rightside frame
        ###@self.cmd_button_frame = customtkinter.CTkFrame(self, width=150, corner_radius=0)
        self.cmd_button_frame = ttk.Frame(self, width=150)
        self.cmd_button_frame.grid(row=0, column=2, rowspan=4, sticky="nsew")
        
        # header for command column
        ###@self.cmd_button_label = customtkinter.CTkLabel(self.cmd_button_frame, text="Commands", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.cmd_button_label = ttk.Label(self.cmd_button_frame, text="Commands")
        self.cmd_button_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # insert command buttons and progress bars
        try:
            row=1
            self.menuitems=self.cmddata["menuitems"]
            for menuitem in self.menuitems:
                if float(self.cmdfileversion) >= 1.0:
                    cmd=menuitem["cmd"]
                    cmdname=menuitem["cmdname"]
                    cmdoutput=menuitem["cmdoutput"]
                else:
                    self.logger.error(f"load_commands(): Unsupported Commandfile version {self.cmdfileversion} in {self.cmdfilename}, assuming 1.0")
                    self.cmdfileversion="1.0"
                    cmd=menuitem["cmd"]
                    cmdname=menuitem["cmdname"]
                    cmdoutput=menuitem["cmdoutput"]

                self.logger.info(f"{row}. Menuitem: {cmdname}: {cmd},{cmdoutput}")
                try:
                    index=self.cmdnames.index(cmdname)
                    if index:
                        self.logger.warning(f"{row}. Menuitem: {cmdname}: {cmd},{cmdoutput}: CMDNAME EXISTS, MUST BE UNIQUE, IGNORING ITEM!")
                        break
                except Exception as err:
                    self.cmdnames.append(cmdname)

                self.cmdoutputs.append(cmdoutput)

                # setup queue
                cmdqueue=queue.Queue(maxsize=GUI_MAXQUEUESIZE)
                self.cmdqueues.append(cmdqueue)

                # add cmd progressbar
                ###@cmdprogressbar = customtkinter.CTkProgressBar(self.cmd_button_frame)
                cmdprogressbar = ttk.Progressbar(self.cmd_button_frame)
                cmdprogressbar.grid(row=row, column=1, padx=20, pady=10)
                cmdprogressbar.configure(mode="indeterminate")
                self.cmdprogressbars.append(cmdprogressbar)

                # add cmd button
                ###@cmdbutton = customtkinter.CTkButton(self.cmd_button_frame, text=cmdname)
                cmdbutton = ttk.Button(self.cmd_button_frame, text=cmdname)
                cmdbutton.grid(row=row, column=0, padx=20, pady=10)
                self.cmdbuttons.append(cmdbutton)
                cmdbutton.configure(command=functools.partial(self.start_command_thread,cmdname,cmd,cmdoutput,cmdqueue))
                
                row+=1

        except Exception as err:
            self.logger.error(f"load_commands(): While parsing cmdfile {self.cmdfilename}, cmdname={cmdname}: Unexpected {err=}, {type(err)=}")
            self.retval=RETVAL_JSON_PARSE_ERROR
            self.destroy()
            return
 

    # load commands
    def load_commands(self):

        self.cmdfilename=os.path.join(os.path.expanduser(self.cmdfiledir),PRGNAME.lower()+".json")
        self.logger.info(f"Commandfile is {self.cmdfilename}...")

        try:
            with open(file=self.cmdfilename,mode="r",encoding=self.encoding) as jsonfile:
                self.cmddata = json.load(jsonfile)
            self.logger.info(self.cmddata)
        except Exception as err:
            self.logger.error(f"While reading cmdfile {self.cmdfilename}: Unexpected {err=}, {type(err)=}")
            self.retval=RETVAL_JSON_PARSE_ERROR
            self.destroy()
            #self.quit()
            return

        jsonfile.close()

        self.cmdfileversion="1.0"
        try:
            self.cmdfileversion=self.cmddata["version"]
            self.logger.info(f"Commandfile version: {self.cmdfileversion}")
        except Exception as err:
            self.logger.info(f"Commandfile version not found in {self.cmdfilename}, assuming: {self.cmdfileversion}")

        try:
            self.menuitems=self.cmddata["menuitems"]
        except Exception as err:
            self.logger.error(f"While getting menuitems from {self.cmdfilename}: Unexpected {err=}, {type(err)=}")
            self.retval=RETVAL_JSON_PARSE_ERROR
            self.destroy()
            #self.quit()
            return

        if self.menuitems == []:
            self.logger.error(f"No menuitems found in {self.cmdfilename}: Unexpected {err=}, {type(err)=}")
            self.retval=RETVAL_NO_MENUITEMS_ERROR
            self.destroy()
            return


    # starting a command in a thread
    def start_command_thread(self,cmdname,cmd,cmdoutput,queue):

        threadid=threading.get_ident()
        thrednativeid=threading.get_native_id()
        self.logger.info(f"Starting command thread {cmdname}, cmd={cmd} (current thread ident={threadid}/nativeid={thrednativeid})...")

        cmdthread=threading.Thread(target=self.run_command,args=[cmdname,cmd,cmdoutput,queue])
        cmdthread.daemon=True # thread dies with the command
        cmdthread.name=cmdname
        self.cmdthreads.append(cmdthread)

        index=self.cmdnames.index(cmdname)
        button=self.cmdbuttons[index]
        progressbar=self.cmdprogressbars[index]

        ###@button.configure(border_width=1)
        ###@button.configure(border_color=['red', 'red'])
        button.configure(state="disabled")

        progressbar.configure(bootstyle="danger-striped")
        progressbar.start()

        cmdthread.start()
        self.logger.info(f"Active Thread count: {threading.active_count()}")

        return


    # run the command imside the thread
    def run_command(self,cmdname,cmd,cmdoutput,queue):

        currentthread=threading.current_thread()
        threadid=currentthread.ident
        thrednativeid=currentthread.native_id
        threadname=currentthread.name
        self.logger.info(f"Starting command {cmdname} in the new thread thread with ident={threadid}/nativeid={thrednativeid}...")

        with self.lock:
            self.cmdretvals[threadid]=0
            msg="I have started..."
            queue.put(
                    {
                        "id": threadid,
                        "cmdname": threadname,
                        "state": "started",
                        "retval": 0,
                        "msg": msg,
                        "timestamp": datetime.datetime.now()
                    }
            )

        # -------------------------------------------------
        # the main task
        # -------------------------------------------------
        self.logger.debug(f"Starting subprocess for cmd {cmd} (cmdoutput={cmdoutput}) in thread {threadname} (current thread ident={threadid}/nativeid={thrednativeid})...")
        if cmdoutput:
            subproc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=None,cwd=None,text=True,encoding=self.encoding,bufsize=1)
            while True:
                line=subproc.stdout.readline()
                if not line:
                    break
                msg=line
                queue.put(
                        {
                            "id": threadid,
                            "cmdname": threadname,
                            "state": "running",
                            "retval": 0,
                            "msg": msg,
                            "timestamp": datetime.datetime.now()
                    }
                )
        else:
            subproc = subprocess.Popen(cmd,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,stdin=None,text=True,encoding=self.encoding,bufsize=1)
            while True:
                line=subproc.stderr.readline()
                if not line:
                    break
                msg=line
                queue.put(
                        {
                            "id": threadid,
                            "cmdname": threadname,
                            "state": "running",
                            "retval": 0,
                            "msg": msg,
                            "timestamp": datetime.datetime.now()
                    }
                )
        subproc.communicate()

        with self.lock:
            time.sleep(0.01)
            # the return value
            retval=subproc.returncode

            self.cmdretvals[threadid]=retval
            self.logger.info(f"Ended thread {threadname}, cmd={cmd} (current thread ident={threadid}/nativeid={thrednativeid})...")
            msg="I have finished!"
            queue.put(
                    {
                        "id": threadid,
                        "cmdname": threadname,
                        "state": "ended",
                        "retval": retval,
                        "msg": msg,
                        "timestamp": datetime.datetime.now()
                    }
            )

            # lets wait before finishing
            time.sleep(0.1)
            self.logger.info(f"Ended command {cmdname} in the thread with ident={threadid}/nativeid={thrednativeid} with retval {retval}")

        return


    # process queues in the main thread
    def process_queues(self) -> int:

        totalqueuesize=0
        for queue in self.cmdqueues:
            queuesize=queue.qsize()
            totalqueuesize+=queuesize

        self.logger.debug(f"Processing Queues ({totalqueuesize} messages queued, active threads: {threading.active_count()})...")

        # there was nothing to do
        if totalqueuesize > 0:
            for queue in self.cmdqueues:
                queuesize=queue.qsize()
                if(queuesize>GUI_MAXQUEUEITEMS):
                    queuesize=GUI_MAXQUEUEITEMS
                i=0
                while i<queuesize:
                    item=queue.get()
                    cmdname=item["cmdname"]
                    index=self.cmdnames.index(cmdname)
                    state=item["state"]
                    timestamp=item["timestamp"]
                    timestampstring=timestamp.strftime("%Y%m%d %H:%m:%S")
                    itemmsg=item["msg"]

                    if state=="ended":
                        self.logger.info(f"Thread has ended: {item}")
                        button=self.cmdbuttons[index]
                        ###@button.configure(border_width=0)
                        ###@button.configure(border_color=['gray', 'gray'])
                        button.bootstyle="light"
                        button.configure(state="normal")

                        progressbar=self.cmdprogressbars[index]
                        progressbar.stop()

                        # workaround to initialize the indeterminate progressbar
                        progressbar.destroy()
                        ###@progressbar = customtkinter.CTkProgressBar(self.cmd_button_frame)
                        progressbar = ttk.Progressbar(self.cmd_button_frame)
                        progressbar.grid(row=index+1, column=1, padx=20, pady=10)
                        progressbar.configure(mode="indeterminate")
                        self.cmdprogressbars[index]=progressbar

                    elif state=="running":
                        self.logger.debug(f"Thread is running: {item}")

                    elif state=="started":
                        self.logger.info(f"Thread has started: {item}")

                    else:
                        self.logger.info(f"Received item with unknown state in cmdqueue: {item}")

                    if itemmsg:
                        for line in itemmsg.splitlines():
                            msg=cmdname+': '+timestampstring+' '+line+'\n'
                            self.sessionlogfile.write(msg)
                            linecount=int(self.textbox.index('end-1c').split('.')[0])
                            ###@self.textbox.configure(state="normal")
                            self.textbox.configure(state="normal")
                            if linecount > GUI_MAXLINEBUFFER:
                                delend=str(GUI_CLEARLINES+1)+'.0'
                                self.logger.debug(f"Linecount: {linecount},{delend}")
                                self.textbox.delete('1.0',delend)
                                self.textbox.insert('1.0','.\n.\n.\n')

                            self.textbox.insert('end',msg)
                            ###@self.textbox.configure(state="disabled")
                            self.textbox.configure(state="disabled")
                    self.textbox.see("end")
                    queue.task_done()

                    i+=1

        totalqueuesize=0
        for queue in self.cmdqueues:
            queuesize=queue.qsize()
            totalqueuesize+=queuesize
        return totalqueuesize


    # check queues in the main thread
    def check_queues(self) -> bool:

        # create the threading lock 
        self.lock=threading.Lock()
        
        # ebug check box
        ##if self.dbgcheckbox.get()==1:
        if self.debug_var==1:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(self.loglevel)

        totalqueuesize=self.process_queues()
        if totalqueuesize>0:
            self.logger.debug(f"{totalqueuesize} messages still queued -> fast refresh ({GUI_REFRESH_FAST}, active threads: {threading.active_count()})...")
            self.after(GUI_REFRESH_FAST,self.check_queues)
        else:
            self.logger.debug(f"{totalqueuesize} messages queued -> slow refresh ({GUI_REFRESH_SLOW},  active threads: {threading.active_count()})...")
            self.after(GUI_REFRESH_SLOW,self.check_queues)



# ==========================================================================================================================
# MAIN
#---------------------------------------------------------------------------------------------------------------------------
# only run this if called a main py file
if __name__ == "__main__":
    app = XmenuApp()
    app.mainloop()
    exit(app.retval[0])

# ==========================================================================================================================
# EOF
# ==========================================================================================================================