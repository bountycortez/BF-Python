import subprocess
import threading
import time
import queue

# Define the command to run
command = 'find /Users/berndflunger/Documents -name "*.png" -print'
#command = 'echo "Hello World!'
print(f'Splitted command: {command.split()}')

# Start the subprocess and store the Popen object
process_queue = queue.Queue()
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0,universal_newlines=True,shell=True)

# Define a function to read from the stdout pipe of the subprocess
def read_stdout_pipe(stdout_pipe):
    while True:
        # Read a line of output from stdout
        line = stdout_pipe.readline()
        if line:
            process_queue.put(line)
            print(f'Found line: {line.strip()}')
        else:
            print('NO MORE OUTPUT! (stout_pipe={stdout_pipe})')
            process_queue.task_done()
            break

# Start a new thread to read from the stdout pipe of the subprocess
#process_queue=queue.Queue(1024)
thread = threading.Thread(target=read_stdout_pipe, daemon=False, args=(process.stdout,))
#time.sleep(3)
thread.start()


# Wait for the subprocess to complete
process.wait()

print(process_queue.join())


# Print the exit code of the subprocess
print(f'Exit code: {process.returncode}')