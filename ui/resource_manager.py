"""Resource manager foundation.

Resolves paths for UI assets (icons, styles, fonts) without loading or
requiring the assets to actually exist yet. This is deliberately a path
resolver only — no icon/font files are added in this Build. See
docs/development/FUTURE_FEATURE_POLICY.md: assets are implemented when a
Build explicitly calls for them.
"""

from pathlib import Path

_ASSETS_ROOT: Path = Path(__file__).parent.parent


class ResourceManager:
    """Resolves expected paths for icons, styles, fonts, and future assets.

    Does not verify that a resolved path exists — callers that need a
    real asset today should check `Path.exists()` themselves. This keeps
    the manager usable now, ahead of any assets being added.
    """

    def get_icon_path(self, name: str) -> Path:
        """Return the expected path for an icon asset.

        Args:
            name: Icon file name, e.g. "chat.svg".

        Returns:
            The path where this icon is expected to live once icon
            assets are added (reserved: `assets/icons/`).
        """
        return _ASSETS_ROOT / "assets" / "icons" / name

    def get_style_path(self, name: str) -> Path:
        """Return the path to a stylesheet in `styles/`.

        Args:
            name: Stylesheet file name, e.g. "dark.qss".

        Returns:
            The path to the requested stylesheet.
        """
        return _ASSETS_ROOT / "styles" / name

    def get_font_path(self, name: str) -> Path:
        """Return the expected path for a font asset.

        Args:
            name: Font file name, e.g. "Inter-Regular.ttf".

        Returns:
            The path where this font is expected to live once font
            assets are added (reserved: `assets/fonts/`).
        """
        return _ASSETS_ROOT / "assets" / "fonts" / name

    def get_asset_path(self, category: str, name: str) -> Path:
        """Return the expected path for a future, uncategorized asset.

        Args:
            category: Asset subcategory, e.g. "sounds", "images".
            name: Asset file name.

        Returns:
            The path where this asset is expected to live under
            `assets/<category>/`.
        """
        return _ASSETS_ROOT / "assets" / category / name
