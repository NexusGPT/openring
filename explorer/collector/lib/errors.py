class SourceError(Exception):
    """A source file is present but cannot be read as expected.

    The runner turns it into status 'unparsed' with `files` in manifest source[] and
    the text of this exception in message.
    """

    def __init__(self, message, files=()):
        super().__init__(message)
        self.files = [files] if isinstance(files, str) else list(files)
