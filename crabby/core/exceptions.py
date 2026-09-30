
class ConfigurationTemplateNotFoundError(RuntimeError):
    """
    Thrown when the configuration template cannot be obtained either locally or remotely.
    """

class UnsupportedPlatformError(RuntimeError):
    """
    Raised when the application is executed on an unsupported operating system.
    """