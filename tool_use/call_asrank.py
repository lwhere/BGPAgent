import subprocess
import fcntl
import os

def write_and_execute_with_lock(file_name, content, command):
    with open(file_name, 'w+') as file:
        # Lock the file for exclusive access
        fcntl.flock(file, fcntl.LOCK_EX)
        try:
            # Write the content to the file
            file.write(content)
            # Ensure the content is written to disk
            file.flush()
            os.fsync(file.fileno())

            # Execute the command while holding the lock
            result = subprocess.run(command, capture_output=True, text=True)
        finally:
            # Unlock the file
            fcntl.flock(file, fcntl.LOCK_UN)
    return result.stdout

def main(input_content):
    # Define the file name
    file_name = 'xx.txt'

    # Command to call asrank.pl script
    command = ['perl', 'asrank.pl', file_name]

    # Write to the file and execute the command with locking
    output = write_and_execute_with_lock(file_name, input_content, command)

    # Return the output
    return output

if __name__ == "__main__":
    # Example input content
    input_content = input()

    # Call the function and get the output
    output = main(input_content)

    # Print the output
    print(output)
