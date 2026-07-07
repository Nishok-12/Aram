##################################
# Built-in functions for Aram
##################################

# Math functions implemented:
# ---------------------------
# sin cos tan
# ceil floor
# pow factorial mod 
# lcm gcd sqrt 
# radians degrees

# Math Constants:
# ---------------
#pi = 3.141592
#e = 2.718281
#tau = 6.283185

# Random Built-in functions implemented:
# --------------------------------------
# randint, choice, random

import error
from sys import exit

def வெளியேறு():
    exit(0)

def வகை(x):
    t = type(x)
    if t == int:
        return 'முழுஎண்'
    elif t == float:
        return 'புள்ளிஎண்'
    elif t == str:
        return 'வாக்கியம்'
    elif t == list:
        return 'பட்டியல்'
    else:
        return 'முழுஎண்ணோ புள்ளிஎண்ணோ வாக்கியமோ பட்டியலோ அல்ல!'

def முழுஎண்(num):
    try:
        return int(num)
    except:
        error.Error("முழுஎண்() - முழுஎண்ணாக மாற்ற இயலவில்லை", str(num))
         

def புள்ளிஎண்(num):
    try:
        return float(num)
    except:
        error.Error("புள்ளிஎண்() - புள்ளிஎண்ணாக மாற்ற இயலவில்லை", str(num))
         

def வாக்கியம்(inp):
    try:
        return str(inp)
    except:
        error.Error("வாக்கியம்() - வாக்கியமாக மாற்ற இயலவில்லை", str(inp))
         

def round(num):
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "round()")
         
    return round(num)

def get_pi():
    return 3.141592

def get_e():
    return 2.718281

def get_tau():
    return 6.283185


def ceil(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "ceil()")
         
    return math.ceil(num)

def floor(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "floor()")
         
    return math.floor(num)

def sin(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "sin()")
         
    return math.sin(num)

def cos(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "cos()")
         
    return math.cos(num)

def tan(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "tan()")
         
    return math.tan(num)

def power(a, b):
    import math
    if type(a) not in [int, float] or type(b) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "power()")
         
    return a ** b

def factorial(num):
    import math
    if num == 0.0:
        num = 0
    if type(num) != int:
        error.Error("பொருந்தாத oவகை உள்ளீடு (எதிர்பார்த்தது முழுஎண்)", "factorial()")
         
    if num < 0:
        error.Error("-ve மதிப்புகளுக்கு factorial வரையறுக்க முடியாது", "factorial()")
         
    return math.factorial(num)

def mod(a, b):
    import math
    if type(a) not in [int, float] or type(b) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "mod()")
         
    if b == 0 or b == 0.0:
        error.Error("கணிதப் பிழை (0 ஆல் வகுக்க முடியாது)", "mod()")
         
    return math.fmod(a, b)

def gcd(a, b):
    import math
    if a == 0.0:
        a = 0
    if b == 0.0:
        b = 0
    if type(a) != int or type(b) != int:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண்)", "gcd()")
         
    return math.gcd(a, b)

def lcm(a, b):
    import math
    if a == 0.0:
        a = 0
    if b == 0.0:
        b = 0
    if type(a) != int or type(b) != int:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண்)", "lcm()")
         
    return math.lcm(a, b)

def sqrt(num):
    import math
    if type(num) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "sqrt()")
         
    if num < 0:
        error.Error("sqrt()ல் உள்ளிட்ட எண் +ve ஆக இருக்க வேண்டும் ")
         
    return math.sqrt(num)

def radians(degrees):
    import math
    if type(degrees) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "radians()")
         
    return math.radian(degrees)

def degrees(radians):
    import math
    if type(radians) not in [int, float]:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண் அல்லது புள்ளிஎண்)", "degrees()")
         
    return math.degrees(radians)


def randint(a, b):
    import random
    if a == 0.0:
        a = 0
    if b == 0.0:
        b = 0
    if type(a) != int or type(b) != int:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது முழுஎண்)", "randint()")
         
    return random.randint(a, b)

def choice(choices):
    import random
    print(choices)
    if type(choices) != list:
        error.Error("பொருந்தாத வகை உள்ளீடு (எதிர்பார்த்தது பட்டியல்)", "choice")
         
    if len(choices) == 0:
        error.Error("பட்டியலில் குறைந்தது 1 element இருக்க வேண்டும்", "choice()")
         
    return random.choice(choices)

def random():
    import random
    # returns a random floating number between 0 and 1
    return random.random()

class AramFile:
    def __init__(self, filename):
        import os
        mode = 'rb+' if os.path.exists(filename) else 'wb+'
        self.file = open(filename, mode)

    def seek(self, pos, whence=0):  
        self.file.seek(pos, whence)

    def read(self, count=-1):
        return self.file.read(count)

    def write(self, data):
        if isinstance(data, str):  # convert to bytes if needed
            data = data.encode("utf-8")
        self.file.write(data)
        self.file.flush()

    def close(self):
        self.file.close()


# Tamil-style functions
def திற(filename):
    return AramFile(filename)

def நிறுத்து(file_obj, pos):
    if isinstance(file_obj, AramFile):
        file_obj.seek(pos)
        return None
    else:
        raise TypeError("Expecting a file object in அடுக்கு()")

def படி(file_obj, count=-1):
    if isinstance(file_obj, AramFile):
        return file_obj.read(count)
    else:
        raise TypeError("Expecting a file object in படிக்க()")

def எழுது(file_obj, data):
    if isinstance(file_obj, AramFile):
        data = data.replace("\\n", "\n")
        data = data.replace("\\t", "\t")
        file_obj.write(data)
        return None
    else:
        raise TypeError("Expecting a file object in எழுத()")

def மூடு(file_obj):
    if isinstance(file_obj, AramFile):
        file_obj.close()
        return None
    else:
        raise TypeError("Expecting a file object in மூடு()")

def துவக்கம்(file_obj):  # rewind
    """Move file pointer to beginning"""
    if isinstance(file_obj, AramFile):
        file_obj.seek(0)
        return None
    else:
        raise TypeError("Expecting a file object in மீள்_துவக்கம்()")

def சேர்க்க(file_obj, data):  # append
    """Write data at the end of file"""
    if isinstance(file_obj, AramFile):
        file_obj.seek(0, 2)  # move to end
        file_obj.write(data)
        return None
    else:
        raise TypeError("Expecting a file object in சேர்க்க()")
    
def உறுப்பு_சேர்க்க(file_obj, data):
    if isinstance(file_obj, AramFile):
        file_obj.seek(0, 2)
        if isinstance(data, str):
            data = data.encode("utf-8")
        file_obj.write(data)
        return None
    else:
        raise TypeError("Expecting a file object in உறுப்பு_சேர்க்க()")

def பிரி(collection, start, stop):
    if isinstance(collection, (list, tuple)):
        return collection[start:stop]
    else:
        error.Error("பிரி() - ஒரு பட்டியல் அல்லது தொகுப்பு எதிர்பார்க்கப்பட்டது")
       
def இணை(c1, c2):
    if isinstance(c1, list) and isinstance(c2, list):
        return c1 + c2
    elif isinstance(c1, tuple) and isinstance(c2, tuple):
        return c1 + c2
    else:
        error.Error("இணை() - இரண்டு பட்டியல்கள் அல்லது இரண்டு தொகுப்புகள் எதிர்பார்க்கப்பட்டன")

def தொடர்(collection, n):
    if isinstance(collection, (list, tuple, str)):
        if not isinstance(n, int):
            error.Error("தொடர்() - ஒரு முழுஎண் எதிர்பார்க்கப்பட்டது")
        return collection * n
    else:
        error.Error("தொடர்() - ஒரு பட்டியல், தொகுப்பு, அல்லது வாக்கியம் எதிர்பார்க்கப்பட்டது")

def உள்ளது(collection, element):
    if not isinstance(collection, (list, tuple, set)):
        error.Error("உள்ளது() - ஒரு பட்டியல், தொகுப்பு, அல்லது கணம் (set) எதிர்பார்க்கப்பட்டது")
    return element in collection

def நீளம்(obj):
    if isinstance(obj, (list, tuple, set, str)):
        return len(obj)
    else:
        error.Error("நீளம்() - ஒரு பட்டியல், தொகுப்பு, கணம் அல்லது வாக்கியம் எதிர்பார்க்கப்பட்டது")

def பட்டியல்_உருவாக்கு(elements):
    if not isinstance(elements, (list, tuple, set)):
        error.Error("பட்டியல்_உருவாக்கு() - ஒரு பட்டியல், தொகுப்பு, அல்லது கணம் (set) எதிர்பார்க்கப்பட்டது")
    return list(elements)

def தொகுப்பு_உருவாக்கு(elements):
    if not isinstance(elements, (list, tuple, set)):
        error.Error("தொகுப்பு_உருவாக்கு() - ஒரு பட்டியல், தொகுப்பு, அல்லது கணம் (set) எதிர்பார்க்கப்பட்டது")
    return tuple(elements)

def கணம்_உருவாக்கு(elements):
    if not isinstance(elements, (list, tuple, set)):
        error.Error("கணம்_உருவாக்கு() - ஒரு பட்டியல், தொகுப்பு, அல்லது கணம் (set) எதிர்பார்க்கப்பட்டது")
    return set(elements)