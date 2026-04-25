import os
from typing import BinaryIO, NamedTuple, Protocol, TypeAlias, runtime_checkable

@runtime_checkable
class ReadSeekBinary(Protocol):
    def read(self, size: int = ...) -> bytes: ...
    def seek(self, offset: int, whence: int = ...) -> int: ...

PathInput: TypeAlias = str | bytes | os.PathLike[str] | os.PathLike[bytes]
FileInput: TypeAlias = PathInput | BinaryIO | ReadSeekBinary

class ImageInfo(NamedTuple):
    width: int
    height: int
    rotation: int
    xdpi: int
    ydpi: int
    colors: int
    channels: int

def get_info(
    filepath: FileInput,
    *,
    size: bool = ...,
    dpi: bool = ...,
    colors: bool = ...,
    exif_rotation: bool = ...,
    channels: bool = ...,
) -> ImageInfo: ...
def get(filepath: FileInput, *, exif_rotation: bool = ...) -> tuple[int, int]: ...
def getDPI(filepath: FileInput) -> tuple[int, int]: ...
