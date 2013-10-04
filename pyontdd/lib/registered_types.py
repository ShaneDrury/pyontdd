class RegisteredCorrelatorTypes:
    """
    A list of registered Correlator types that can be accessed by various functions/classes.
    Initially empty, this is populated by pyontdd.lib.register.registerCorrelator(cls) as a decorator.
    """
    types = {}


class RegisteredDataHandlerTypes:
    """
    A list of registered Data Handler types that can be accessed by various functions/classes.
    Initially empty, this is populated by pyontdd.lib.register.registerDataHandler(cls) as a decorator
    """
    types = {}


class RegisteredFileFormats:
    """
    A list of registered File formats that can be accessed by various functions/classes.
    Initially empty, this is populated by pyontdd.lib.register.registerFileFormat(cls) as a decorator
    """
    types = {}