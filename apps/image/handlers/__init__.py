from glob import glob1
from types import FunctionType
import os

def import_handler(dirname, view_prefix=None):
    for filename in glob1(dirname, '*.py'):
        if filename == '__init__.py':    # I assume you don't want that
            continue

        module_name = os.path.basename(filename).split('.py')[0]

        # You might need to change this, depending on where you run the file:
        imported_module = __import__("%s.%s" % (__package__, module_name), fromlist=[module_name,])

        idict = imported_module.__dict__

        for method_name in idict.get('__all__', idict.keys()):
            method = idict[method_name]
            if not isinstance(method, FunctionType):
                continue
            if view_prefix and not method_name.startswith(view_prefix):
                continue
            globals()[method_name] = method

import_handler(os.path.dirname(__file__))
