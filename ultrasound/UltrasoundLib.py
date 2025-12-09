import RPi.GPIO as GPIO
import time

class UltrasoundLib:
    def __init__(self, trig_pin, echo_pin):
        
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        self.initialize_device()
        
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
        print(f"Distance: {distance} cm")
        # Sleep for a short time before measuring again
        time.sleep(0.1)

        return distance

    def uninitialize_device(self):
            GPIO.cleanup()  # Clean up the GPIO pins on exit



u = UltrasoundLib(trig_pin=23, echo_pin=24)
try:
    while True:
        avg_distance = u.get_average_distance(samples=5)
        print(f"Average Distance: {avg_distance} cm")
        time.sleep(1)
except KeyboardInterrupt:
    print("Measurement stopped by user")
    u.uninitialize_device()