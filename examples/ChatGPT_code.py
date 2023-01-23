import tkinter as tk
import subprocess
import threading
import select
import fcntl
import os


class App:
    def __init__(self, master):
        self.master = master
        self.commands = ['find /Users/berndflunger/Documents -name "*.txt" -print', 'find /Users/berndflunge/Documents -name "*.png" -print', 'find /Users/berndflunger/Documents -name "*.jpg" -print']
        self.buttons = []
        self.processes = []

        # Create a Text widget to display the output
        self.text = tk.Text(master)
        self.text.pack()

        # Create a button for each command
        for command in self.commands:
            button = tk.Button(master, text=command, command=lambda c=command: self.run_command(c))
            button.pack()
            self.buttons.append(button)


    def run_command(self, command):
        print(f'run_command(): command={command}')
           # Update the button text to show that the command is running
        button = self.buttons[self.commands.index(command)]
        button['text'] = 'Running...'
        button['state'] = 'disabled'
        button.configure(fg='blue')

        # Start the subprocess and store the Popen object
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1000)
        self.processes.append(process)

        # Start a new thread to read from the PIPE object
        thread = threading.Thread(target=self.read_pipe_thread, args=(process.stdout,process.stderr,button,command,process))
        thread.start()

    def read_pipe_thread(self, stdout_pipe, stderr_pipe, button, command, process):
        print(f'read_pipe_thread(): command={command}')
        # Set the pipes as non-blocking
        fcntl.fcntl(stdout_pipe, fcntl.F_SETFL, fcntl.fcntl(stdout_pipe, fcntl.F_GETFL) | os.O_NONBLOCK)
        fcntl.fcntl(stderr_pipe, fcntl.F_SETFL, fcntl.fcntl(stderr_pipe, fcntl.F_GETFL) | os.O_NONBLOCK)

        # Create a list of the pipes to multiplex
        pipes = [stdout_pipe, stderr_pipe]

        # Multiplex the pipes and update the Text widget with the output
        while pipes:
            readable, _, _ = select.select(pipes, [], [])
            for pipe in readable:
                line = pipe.readline()
                if line:
                    self.text.insert('end', line)
                    self.master.update()
                    print(f'Received output from stdout: {line.strip()}')
                else:
                    pipes.remove(pipe)
        stdout_pipe.close()
        stderr_pipe.close()

        # Check the exit value of the subprocess
        exit_value = process.poll()
        print(f"Command {command}, Exitvalue: {exit_value}")
        if exit_value is not None:
            # Update the button text to show the command that was run
            button['text'] = f'{command} ({exit_value})'
            if exit_value != 0:
                # Set the background color of the button to red if the subprocess exited with a non-zero exit code
                button.configure(fg='red')
            else:
                # Update the button text to show the command that was run
                button['text'] = command
                button.configure(fg='green')

            button['state'] = 'normal'

root = tk.Tk()
app = App(root)
root.mainloop()

