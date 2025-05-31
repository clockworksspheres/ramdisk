import psutil
import os


def get_current_user_id():
    # Get the current process
    process = psutil.Process(os.getpid())

    # Get the user ID of the process
    user_id = process.username()

    return user_id


user_id = get_current_user_id()
print(f"User ID: {user_id}")

