import random  # Import the entire random module
import threading
import time

class TaskThread:
    def __init__(self, timeout=5):
        self.result = None
        self._lock = threading.Lock()
        self._event = threading.Event()  # Event flag for stopping the thread
        self._timeout = timeout  # Timeout for the thread
        self._callback = None  # Callback function to be called when task completes
        self._thread = threading.Thread(target=self._taskA)

    def _get_average_distance(self, samples=5):
        time.sleep(0.4)
        return random.uniform(1.0, 400.0)  # Simulated distance in cm

    def _taskA(self):
        start_time = time.time()
        while not self._event.is_set():
            # Simulate task processing
            result = self._get_average_distance(samples=3)
            with self._lock:
                self.result = result
                if self._callback:
                    self._callback(result)  # Call the callback with the result

            time.sleep(0.3)  # Delay between measurements

            # Check if timeout occurred
            if time.time() - start_time >= self._timeout:
                with self._lock:  # Thread-safe result modification
                    self.result = "Timeout reached after calculating distances"
                print("Timeout occurred!")
                self._event.set()  # Stop the thread on timeout
                if self._callback:
                    self._callback(self.result)  # Call the callback on timeout
                break

    def start(self):
        self._thread.start()

    def stop(self):
        self._event.set()  # Trigger stop condition for the thread
        self._thread.join()  # Wait for the thread to finish execution

    def register_callback(self, callback):
        """Register a callback function to be called when the thread ends"""
        self._callback = callback

    def get_result(self):
        """Thread-safe access to the result"""
        with self._lock:
            return self.result

# Example usage:
def on_task_complete(result):
    print(f"Task completed with result: {result}")

# Create the TaskThread with a 5-second timeout
task = TaskThread(timeout=5)
task.register_callback(on_task_complete)

# Start the task in a separate thread
task.start()

try:
    # Main thread work, can simulate other work here
    time.sleep(10)  # Simulate some time before stopping 
    task.stop()
except KeyboardInterrupt:
    # Handle manual interruption, e.g., Ctrl+C
    print("Main thread interrupted. Stopping task.")
    task.stop()

# Wait for the thread to complete
print("Main program finished.")
