"""Reference solutions for greet_device."""


# Best practice: an f-string reads like the output it produces.
def greet_device(hostname: str, os_name: str, ram_gb: int) -> str:
    return f"Hello, {hostname}! You are running {os_name} with {ram_gb} GB of RAM."


# Also fine: str.format. You will meet it in older code bases.
def greet_device_format(hostname: str, os_name: str, ram_gb: int) -> str:
    return "Hello, {}! You are running {} with {} GB of RAM.".format(hostname, os_name, ram_gb)
