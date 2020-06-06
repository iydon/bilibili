[![PyPI version](https://badge.fury.io/py/iydon.svg)](https://pypi.org/project/iydon/)

*Iydon* is a Python package that provides some personal api for Iydon.

* * *
```
██╗██╗   ██╗██████╗  ██████╗ ███╗   ██╗
██║╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗  ██║
██║ ╚████╔╝ ██║  ██║██║   ██║██╔██╗ ██║
██║  ╚██╔╝  ██║  ██║██║   ██║██║╚██╗██║
██║   ██║   ██████╔╝╚██████╔╝██║ ╚████║
╚═╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝
```
* * *

# Basic Usage
## Installation
Install with pip:
```shell
pip install iydon
```

Get started:
```shell
python -m iydon
```


## Deploy Environment
```Python
from iydon import deploy

deploy.python_packages(ask=False, basic=True, research=True)
```


## Basic Information
```Python
from iydon import info

print(info.as_dict())
print(info.as_namedtuple())
```


## Sites Information
```Python
from iydon import sites

print(sites.get_all_links(full=True))
```


## Symbols
```Python
from iydon import symbols

_locals = locals()
_locals[symbols.pi] = hash(float('inf')) / 10**5
print(π)
```
