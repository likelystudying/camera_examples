import RPi.GPIO as GPIO
import time
import threading


class UltrasoundLib(threading.Thread):
    def __init__(self, trig_pin, echo_pin, timeout=5):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        self.initialize_device()
        self.result = None

        self._event = threading.Event()  # Event flag for stopping the thread
        self._timeout = timeout
        self._callback = None
        self._thread = threading.Thread(target=self._taskA)
        self.result = None  # Initialize result as None
        self._lock = threading.Lock()  # Lock for thread-safe access to result


        
    def initialize_device(self):
        trig = self.trig_pin
        echo = self.echo_pin
        # Code to initialize the ultrasound device
        GPIO.setmode(GPIO.BCM)
        # Define the GPIO pins connected to the sensor
        # Trigger pin
        # Echo pin (input, through voltage divider)

        # Set up the GPIO pins
        GPIO.setup(trig, GPIO.OUT)  # Trigger pin as output
        GPIO.setup(echo, GPIO.IN)   # Echo pin as input

        # Ensure the trigger is initially off
        GPIO.output(trig, False)
        # Allow the sensor to settle
        time.sleep(2)
        
    def get_average_distance(self, samples=5):
        total_distance = 0
        for _ in range(samples):
            distance = self.capture_distance()
            total_distance += distance
        average_distance = total_distance / samples
        return average_distance

    def capture_distance(self):
        trig = self.trig_pin
        echo = self.echo_pin
        distance = 0

        # Send a short pulse to the Trigger pin
        GPIO.output(trig, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(trig, False)

        # Measure the time it takes for the Echo pin to go HIGH and then LOW
        while GPIO.input(echo) == 0:
            pulse_start = time.time()

        while GPIO.input(echo) == 1:
            pulse_end = time.time()

        # Calculate the distance based on the time of flight of the sound wave
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Speed of sound is 34300 cm/s, divide by 2
        distance = round(distance, 2)  # Round to 2 decimal places

        # Print the distance
       # print(f"Distance: {distance} cm")
        # Sleep for a short time before measuring again
        time.sleep(0.1)

        return distance

    def uninitialize_device(self):
        GPIO.cleanup()  # Clean up the GPIO pins on exit

    def _taskA(self):
        start_time = time.time()
        while not self._event.is_set():
            # Get the average distance
            result = self.get_average_distance(samples=4)
            print(f"Average distance: {result:.2f} cm")  # Print or store result

            # Set result and trigger callback if ready
            with self._lock:
                self.result = result
                if self._callback:
                    self._callback(result)  # Call the callback with the result

            time.sleep(0.5)  # Delay between measurements

            # Timeout check
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
        """Stop the thread and automatically join it"""
        self._event.set()  # Trigger stop condition for the thread
        self._thread.join()  # Wait for the thread to finish execution

    def register_callback(self, callback):
        """Register a callback function to be called when the thread ends"""
        self._callback = callback

    def get_result(self):
        """Thread-safe access to the result"""
        with self._lock:
            return self.result

def on_task_complete(result):
    """Callback function that gets called when a result is available"""
    print(f"Task completed with result: {result}")

def test_ultrasound():
    trig_pin = 23  # Example GPIO pin for trigger
    echo_pin = 24  # Example GPIO pin for echo

    # Create the ultrasound task with a timeout of 5 seconds
    ultrasound_task = UltrasoundLib(trig_pin=trig_pin, echo_pin=echo_pin, timeout=5)
    ultrasound_task.register_callback(on_task_complete)

    # Start the task in a separate thread
    ultrasound_task.start()

    try:
        # Main thread work, can simulate other work here
        time.sleep(3)  # Simulate some time before stopping
        print("Stopping the task from the main thread.")
        ultrasound_task.stop()  # This will stop the task and automatically join the thread

    except KeyboardInterrupt:
        # Handle manual interruption, e.g., Ctrl+C
        print("Main thread interrupted. Stopping task.")
        ultrasound_task.stop()

    # Access the result of the task
    print(f"Task Result: {ultrasound_task.get_result()}")

    # Cleanup GPIO after the task is finished
    ultrasound_task.uninitialize_device()

# Run the test
if __name__ == "__main__":
    test_ultrasound()