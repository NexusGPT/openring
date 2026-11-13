"""STEP -> GLB (glTF Y-up, mm), reused by the case extractor. Needs build123d (the design venv has it);
the import is lazy so a plain python can still load this package."""
from pathlib import Path

from . import glb


def step_to_glb(step_path, glb_path):
    """Write glb_path from the STEP file; the file is converted to the bundle's Y-up convention."""
    from build123d import export_gltf, import_step  # noqa: PLC0415

    shape = import_step(str(step_path))
    export_gltf(shape, str(glb_path), binary=True)
    js, binary = glb.read(glb_path)
    if glb.to_y_up(js):
        glb.write(glb_path, js, binary)
    return Path(glb_path)
