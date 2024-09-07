class CameraLibError(Exception):
    """Generic catch-all exception. All custom exceptions in cameralib inherit from it."""
    pass

class InvalidArgError(Exception):
    """Invalid argument passed to function"""
    pass

class GeoError(CameraLibError):
    """A georeferencing related error"""
    pass

class OutOfBoundsError(CameraLibError):
    """The computation cannot complete because coordinates are out of bounds"""
    pass