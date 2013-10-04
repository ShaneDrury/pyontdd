from pyontdd.lib.registered_types import RegisteredCorrelatorTypes, RegisteredDataHandlerTypes, RegisteredFileFormats
__author__ = 'srd1g10'


def registerCorrelator(f):
    """
    Decorator to register a correlator type with the ones that CorrelatorFactory will search through.
    """
    a = RegisteredCorrelatorTypes.types
    if f.__name__ not in a:  # Avoid duplicates
        a.update({f.__name__: f})
    return f


def registerDataHandler(f):
    """
    Decorator to register a data handler type with the ones that DataHandlerFactory will search through.
    """
    a = RegisteredDataHandlerTypes.types
    if f.__name__ not in a:  # Avoid duplicates
        a.update({f.__name__: f})
    return f


def registerFileFormat(f):
    """
    Decorator to register a file format with the ones that FileFactory will search through.
    """
    a = RegisteredFileFormats.types
    if f.__name__ not in a:  # Avoid duplicates
        a.update({f.__name__: f})
    return f

