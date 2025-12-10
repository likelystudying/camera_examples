import threading
import time

class MyThreadedClass:
    def __init__(self):
        self.result = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None

    def _threaded_task(self, data, callback_method):
        """
        The actual task to be executed in a separate thread.
        It takes data and a callback method as arguments.
        """
        print(f"Thread started with data: {data}")
        # Simulate cancellable work: check stop event periodically
        total = 2.0
        interval = 0.1
        elapsed = 0.0
        while elapsed < total:
            if self._stop_event.is_set():
                print("Thread received stop signal. Exiting early.")
                return
            # Wait for interval or until stop event is set
            self._stop_event.wait(interval)
            elapsed += interval

        processed = f"Processed: {data}"
        with self._lock:
            self.result = processed
        print(f"Thread finished. Result: {self.result}")
        if callback_method:
            callback_method(self.result)

    def start_threaded_operation(self, data, callback_func=None):
        """
        Starts a new thread to perform an operation and optionally calls a callback.
        """
        # Create a thread, targeting the internal _threaded_task method.
        # Pass the data and the provided callback function (or a default if none).
        # Reset stop flag for this new run
        self._stop_event.clear()
        thread = threading.Thread(target=self._threaded_task, args=(data, callback_func))
        thread.daemon = True  # may be killed mid-sleep if main dead
        thread.start()
        self._thread = thread
        print("Thread operation initiated.")
        return thread

    def stop_threaded_operation(self, wait=True, timeout=None):
        """Signal the running thread to stop.

        - `wait` (bool): if True, call `join()` on the thread after signalling.
        - `timeout` (float|None): maximum seconds to wait in `join()`.
        """
        self._stop_event.set()
        if self._thread is not None and wait:
            self._thread.join(timeout)
            if self._thread.is_alive():
                print("Warning: thread did not stop within timeout.")

    def on_thread_completion(self, thread_result):
        """
        A callback method within the class to handle the thread's completion.
        """
        print(f"Callback received in the class: {thread_result}")
        # You can perform further actions here based on the thread_result

    def get_result(self):
        """Thread-safe accessor for `self.result`. Returns the current value."""
        with self._lock:
            return self.result

"""Demo: start a cancellable threaded operation and stop it early."""

def stop_example():
    my_instance = MyThreadedClass()

    print("--- Demo: Start stoppable operation ---")
    t = my_instance.start_threaded_operation("Demo stoppable", my_instance.on_thread_completion)

    # Let the job run briefly then request stop
    time.sleep(0.5)
    print("Requesting stop from main...")
    my_instance.stop_threaded_operation(wait=True, timeout=1.0)

    print("After stop, result:", my_instance.get_result())

def callback_example1():
    my_instance = MyThreadedClass()

    # Option 1: Using a method of the same class as a callback
    print("--- Starting Threaded Operation with Class Method Callback ---")
    t = my_instance.start_threaded_operation("Hello from main!", my_instance.on_thread_completion)
    # If the result is important, wait for the thread to finish instead of sleeping
    t.join()
    print("Result after join:", my_instance.get_result())


def callback_example2():
    my_instance = MyThreadedClass()

    # Option 2: Using a separate function as a callback
    def external_callback(result):
        print(f"External callback received: {result}")

    print("\n--- Starting Threaded Operation with External Function Callback ---")
    t2 = my_instance.start_threaded_operation("Another task", external_callback)
    # Alternatively, if this can be background work you don't need to block for, don't join.
    # t2.join()
    # Or poll safely:
    time.sleep(0.1)
    print("Polled result (may be None if not finished):", my_instance.get_result())

def polling_example():
    my_instance = MyThreadedClass()

    print("--- Starting Threaded Operation with Polling ---")
    t3 = my_instance.start_threaded_operation("Polling task")

    # Poll for result every 0.2 seconds
    while t3.is_alive():
        print("Thread is still running...")
        time.sleep(0.2)

    print("Thread completed. Final result:", my_instance.get_result())


if __name__ == '__main__':
    
    stop_example()
    callback_example1()
    callback_example2()
    polling_example()


