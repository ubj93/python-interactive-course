"""Convert between snake_case and camelCase.

The MDM API speaks camelCase ("lastCheckInTime") and our reporting database
speaks snake_case ("last_check_in_time"). Write two functions that convert names
between them.

`snake_to_camel(name)`
- words are separated by one or more underscores
- leading and trailing underscores are dropped
- every word is lowercased; the first word stays lowercase, the others get an
  uppercase first letter
- digits are ordinary characters: "v2_build" -> "v2Build"
- an empty string, or one made only of underscores, gives ""

`camel_to_snake(name)`
- a lowercase-to-uppercase transition starts a new word: "deviceName" -> "device_name"
- a digit-to-uppercase transition also starts a new word: "v2Build" -> "v2_build"
- a run of uppercase letters is one word (an acronym); the run ends where a capital
  is followed by a lowercase letter: "deviceID" -> "device_id",
  "IPAddress" -> "ip_address", "HTTPSProxy" -> "https_proxy"
- the result is entirely lowercase
- a name with no capitals is returned unchanged; "" gives ""

Do not use str.title(): it capitalises after digits and would turn "v2a" into "V2A".

Examples:
    >>> snake_to_camel("last_check_in_time")
    'lastCheckInTime'
    >>> snake_to_camel("__OS_VERSION__")
    'osVersion'
    >>> camel_to_snake("lastCheckInTime")
    'last_check_in_time'
    >>> camel_to_snake("deviceID")
    'device_id'
"""
import re


def snake_to_camel(name: str) -> str:
    raise NotImplementedError("write snake_to_camel")


def camel_to_snake(name: str) -> str:
    raise NotImplementedError("write camel_to_snake")
