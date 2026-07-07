
#######################
# Code to print errors
#######################

# Define a custom exception for Aram language errors
class AramException(Exception):
    pass

class Error:
    def __init__(self, description, char=None):
        if char is not None:
            message = f'\n{description}: {char}'
        else:
            message = f'\n{description}'
        
        print(message)
        # CRITICAL FIX: Raise an exception so that try/except blocks can catch it.
        raise AramException(message)