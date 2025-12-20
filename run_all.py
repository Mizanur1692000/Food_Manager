import multiprocessing
import subprocess
import sys
import os

def run_process(command, log_prefix):
    """Function to run a command as a subprocess and stream its output."""
    try:
        print(f"Starting {log_prefix}...")
        # Use Popen and allow its output to stream directly to the parent's console
        process = subprocess.Popen(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        # Wait for the process to complete
        process.wait()
        if process.returncode != 0:
            print(f"{log_prefix} terminated with a non-zero exit code: {process.returncode}")

    except FileNotFoundError:
        print(f"Error: Command for {log_prefix} not found. Make sure it is installed and in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred while running {log_prefix}: {e}")


if __name__ == "__main__":
    # Define commands for the processes
    fastapi_command = [sys.executable, "-m", "uvicorn", "api_server:app", "--host", "127.0.0.1", "--port", "8000"]
    streamlit_command = [sys.executable, "-m", "streamlit", "run", "app.py"]

    # Create two processes using multiprocessing to run our function
    fastapi_process = multiprocessing.Process(target=run_process, args=(fastapi_command, "FastAPI Server"))
    streamlit_process = multiprocessing.Process(target=run_process, args=(streamlit_command, "Streamlit App"))

    # Start the processes
    fastapi_process.start()
    streamlit_process.start()

    print("Both FastAPI and Streamlit processes have been started.")
    print("You can stop them by closing this terminal (Ctrl+C).")

    # Wait for the processes to complete.
    # If one process fails, we might want to terminate the other.
    try:
        fastapi_process.join()
        streamlit_process.join()
    except KeyboardInterrupt:
        print("\nTerminating processes...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.join()
        streamlit_process.join()
        print("Processes terminated.")
