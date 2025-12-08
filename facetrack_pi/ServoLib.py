import sys
import select
import time

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio

#must call sudo pipgiod daemon ?

# -------------------------
# Non-blocking input helper
# -------------------------
def kbhit():
    return select.select([sys.stdin], [], [], 0)[0]
 
# -------------------------
# Servo using gpiozero + pigpio backend
# -------------------------

class ServoLib:
	def __init__(self, name, servo_pin):

		self.pi = pigpio.pi()
		if not self.pi.connected:
			raise RuntimeError("Cannot connect to pigpio daemon. Run 'sudo pigpiod'")

		self.servo_pin = servo_pin
		self.factory = PiGPIOFactory()

		self.servo = Servo(
			servo_pin,
			pin_factory=self.factory,
			min_pulse_width=0.0005,   # 500 µs
			max_pulse_width=0.0025    # 2500 µs
		)
		self.current_angle = 90
		self.set_angle(90)
		return
		
	def angle_to_value(self, angle):
		"""conver 0-180 to servo vallue -1...1"""
		value = (angle-90)/90.0
		return max(-1, min(1,value))
	
	def set_angle(self, target_angle, steps=20, delay=0.01):
		if not 0 <= target_angle <= 180:
			raise ValueError("Angle must be between 0 and 180")

		if steps < 1:
			steps = 1

		step_angle = (target_angle - self.current_angle) / float(steps)

		for step in range(steps):
			self.current_angle += step_angle
			self.servo.value = self.angle_to_value(self.current_angle)
			time.sleep(delay)

		self.current_angle = target_angle
		self.servo.value = self.angle_to_value(target_angle)
		return

	def stop_servo(self):
		self.servo.detach()
		self.pi.stop()
		
	def __del__(self):
		self.stop_servo()
		
		
def test():
	angle = 100
	name = "tester"
	servo_pin = 18
	s = ServoLib(name, servo_pin)
	s.set_angle(angle)
	s.stop_servo()
	return

def test2():
	#initialization
	angle = 100
	name = "tester"
	servo_pin = 18
	s = ServoLib(name, servo_pin)


	print("press angle(0-180): ")
	while True:
		if kbhit():
			cmd = sys.stdin.readline().strip()
			if not cmd:
				continue
			print(f"input: {cmd}")
	
			if cmd.isdigit():
				angle = int(cmd)
				if 0 <=angle<=180:
					s.set_angle(angle)
				else:
					print("angle oor (0-180)")
			elif cmd.lower()=="q":
				break
			else:
				print("not supported")

	s.stop_servo()
	return


#problem
#servo jitter
#solution
#software controlled servo has a lot of jitter.
#ways to solve the jitter
# - use capacitor                       <- not tried
# - use an external power supply        <- this didn't help much
# - use hardware pwm with GPIOfactory   <- this worked


#todo
# x write servo
# x write opencv
# fix red
# add opencv face detection
# x cleanup servo
# cleanup opencv
# test
# integrate
