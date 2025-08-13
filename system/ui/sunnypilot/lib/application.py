from openpilot.system.ui.lib.application import GuiApplication
from importlib.resources import as_file, files

ASSETS_DIR_SP = files("openpilot.sunnypilot.selfdrive").joinpath("assets")

class GuiApplicationSP(GuiApplication):

    def __init__(self, width: int, height: int):
        super().__init__(width, height)

    def sp_texture(self, asset_path: str, width: int, height: int, alpha_premultiply=False, keep_aspect_ratio=True):
        cache_key = f"{asset_path}_{width}_{height}_{alpha_premultiply}{keep_aspect_ratio}"
        if cache_key in self._textures:
            return self._textures[cache_key]

        with as_file(ASSETS_DIR_SP.joinpath(asset_path)) as fspath:
            texture_obj = self._load_texture_from_image(fspath.as_posix(), width, height, alpha_premultiply, keep_aspect_ratio)
        self._textures[cache_key] = texture_obj
        return texture_obj

gui_app_sp = GuiApplicationSP(2160, 1080)
