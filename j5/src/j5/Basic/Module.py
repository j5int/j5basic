#!/usr/bin/env python

import logging
import inspect
import sys
import os
import traceback

importedmodules = {}

def resolvemodule(modulename, loglevel=logging.WARN):
    """Imports a.b.c as far as possible then returns the value of a.b.c.d.e"""
    if importedmodules.has_key(modulename):
        logging.debug("Returning cached object %s for %s" % (importedmodules[modulename],modulename))
        return importedmodules[modulename]

    try:
        parentmodule = getimportablemodule(modulename)
    except (ImportError, SyntaxError), e:
        logging.log(loglevel, "Could not import module for %s" % (modulename))
        raise AttributeError(str(e))
    logging.debug("parentmodule for %s is %s" % (modulename, str(parentmodule)))
    try:
        module = getpart(parentmodule, modulename)
    except AttributeError, e:
        logging.log(loglevel, "Could not resolve modulename %s" % (modulename))
        raise
    importedmodules[modulename] = module
    logging.debug("Returning object %s for %s" % (module, modulename))
    return module

def canonicalize(path):
    """returns the canonical reference to the path that can be used for comparison to other paths"""
    return os.path.normpath(os.path.realpath(os.path.abspath(path)))

thisfilename = canonicalize(__file__)
if thisfilename.endswith(".pyc") or thisfilename.endswith(".pyo"):
    thisfilename = thisfilename[:-1]

def getimportablemodule(modulename):
    """Attempts to import successive modules on the a.b.c route - first a.b.c, then a.b, etc"""
    components = modulename.split('.')
    module = None
    currentattempt = len(components)
    errormessage = ""
    while currentattempt > 0:
        try:
            attemptedname = '.'.join(components[:currentattempt])
            module = __import__(attemptedname)
            return module
        except ImportError, error:
            # if the ImportError originated from outside this file then raise it, otherwise continue
            cls, exc, trc = sys.exc_info()
            filename, line_number, function_name, text = traceback.extract_tb(trc, 10)[-1]
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                filename = filename[:-1]
            # need to compare to the canonical version of this filename - and make it case insensitive for windows drive letters
            if canonicalize(filename).lower() != thisfilename.lower():
                logging.warning("Import Error attempting to import %s (%s), comes from file %s which seems to be a real module that can't be imported" % (attemptedname, error, filename))
                raise
            logging.debug("Import Error attempting to import %s: %s" % (attemptedname, error))
            currentattempt -= 1
            errormessage = error
        except Exception, error:
            logging.debug("Error attempting to import %s: %s" % (attemptedname, error))
            raise
    raise ImportError("Error importing module %r: %s\nPython path is %r" % (modulename, errormessage, sys.path))

def getpart(module, partname):
    components = partname.split('.')
    for component in components[1:]:
        logging.debug("Getting part %s from module %s" % (component, str(module)))
        module = getattr(module, component)
    return module


