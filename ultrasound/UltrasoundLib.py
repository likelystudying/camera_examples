import RPi.GPIO as GPIO
import time

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins connected to the sensor
TRIG = 23  # Trigger pin
ECHO = 24  # Echo pin (input, through voltage divider)

# Set up the GPIO pins
GPIO.setup(TRIG, GPIO.OUT)  # Trigger pin as output
GPIO.setup(ECHO, GPIO.IN)   # Echo pin as input

# Ensure the trigger is initially off
GPIO.output(TRIG, False)

# Allow the sensor to settle
time.sleep(2)



try:
    while True:
        # Send a short pulse to the Trigger pin
        GPIO.output(TRIG, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIG, False)

        # Measure the time it takes for the Echo pin to go HIGH and then LOW
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # Calculate the distance based on the time of flight of the sound wave
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Speed of sound is 34300 cm/s, divide by 2
        distance = round(distance, 2)  # Round to 2 decimal places

        # Print the distance
        print(f"Distance: {distance} cm")

        # Sleep for a short time before measuring again
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()  # Clean up the GPIO pins on exit
