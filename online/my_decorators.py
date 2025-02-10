#%% Decorators
import functools
import time

"""
# A template 
def decorator(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        value = func(*args, **kwargs)
        # Do something after
        return value
    return wrapper_decorator
"""

def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__}() in {run_time:.4f} secs")
        return value

    return wrapper_timer


def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(value)}")
        return value

    return wrapper_debug


PLUGINS = dict()

def register(func):
    """Register a function as a plug-in"""
    PLUGINS[func.__name__] = func
    return func

#%% test
if __name__ == "__main__":
    # debug  (own function)
    @debug
    def make_greeting(name, age=None):
        if age is None:
            return f"Howdy {name}!"
        else:
            return f"Whoa {name}! {age} already, you're growing up!"

    print('something') 
    make_greeting("Benjamin")
    make_greeting("Benjamin", age=32)

    # debug  (imported function)
    import math
    math.factorial = debug(math.factorial)

    def approximate_e(terms=18):
        return sum(1 / math.factorial(n) for n in range(terms))
    
    approximate_e(terms=5)

    # register
    @register
    def say_hello(name):
        return f"Hello {name}"


    @register
    def be_awesome(name):
        return f"Yo {name}, together we're the awesomest!"
    

    print(PLUGINS)
    print(globals())