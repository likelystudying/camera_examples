from temp import MyThreadedClass
import time

"""Demo: start a cancellable threaded operation and stop it early."""

def main():
    my_instance = MyThreadedClass()

    print("--- Demo: Start stoppable operation ---")
    t = my_instance.start_threaded_operation("Demo stoppable", my_instance.on_thread_completion)

    # Let the job run briefly then request stop
    time.sleep(0.5)
    print("Requesting stop from main...")
    my_instance.stop_threaded_operation(wait=True, timeout=1.0)

    print("After stop, result:", my_instance.get_result())


if __name__ == '__main__':
    main()
