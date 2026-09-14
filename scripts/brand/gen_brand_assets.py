"""Generate Open WebUI assets from the official DevAgent.Dev CI v2 artwork.

The source files already contain approved transparency, spacing, colours, and
reverse variants. This script only resizes or copies them; it never reconstructs
the logo, removes backgrounds, or recolours artwork.
"""

import os
import shutil
import sys
from pathlib import Path

from PIL import Image


BRAND_ROOT = Path(
    os.environ.get(
        "DEVAGENT_BRAND_ASSETS",
        Path.home() / "DevAgent.Dev" / "brand-assets",
    )
).expanduser()
OUTPUTS = (
    [Path(sys.argv[1])]
    if len(sys.argv) > 1
    else [Path("static/static"), Path("backend/open_webui/static")]
)

ICON_SOURCE = BRAND_ROOT / "logo-sizes" / "devagent-icon-master.png"
SYMBOL_SOURCE = (
    BRAND_ROOT / "transparent" / "png" / "devagent-symbol-color-transparent.png"
)
SYMBOL_REVERSE_SOURCE = (
    BRAND_ROOT / "transparent" / "png" / "devagent-symbol-white-transparent.png"
)
COMPACT_SOURCE = (
    BRAND_ROOT / "transparent" / "png" / "devagent-compact-color-transparent.png"
)
COMPACT_REVERSE_SOURCE = (
    BRAND_ROOT / "transparent" / "png" / "devagent-compact-white-transparent.png"
)
HORIZONTAL_SOURCE = (
    BRAND_ROOT / "transparent" / "png" / "devagent-horizontal-color-transparent.png"
)
FAVICON_SVG_SOURCE = BRAND_ROOT / "svg" / "devagent-app-icon.svg"


def require_sources() -> None:
    missing = [
        path
        for path in (
            ICON_SOURCE,
            SYMBOL_SOURCE,
            SYMBOL_REVERSE_SOURCE,
            COMPACT_SOURCE,
            COMPACT_REVERSE_SOURCE,
            HORIZONTAL_SOURCE,
            FAVICON_SVG_SOURCE,
        )
        if not path.is_file()
    ]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing official DevAgent.Dev brand assets:\n{formatted}")


def resize_square(source: Path, size: int, destination: Path) -> Image.Image:
    image = (
        Image.open(source)
        .convert("RGBA")
        .resize((size, size), Image.Resampling.LANCZOS)
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, optimize=True)
    print("wrote", destination, image.size)
    return image


def resize_to_width(source: Path, width: int, destination: Path) -> None:
    image = Image.open(source).convert("RGBA")
    height = round(image.height * width / image.width)
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, optimize=True)
    print("wrote", destination, image.size)


def copy_asset(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    print("wrote", destination)


def generate_assets(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)

    # The approved square app icon already includes the maskable safe zone.
    resize_square(ICON_SOURCE, 512, output / "favicon.png")
    resize_square(ICON_SOURCE, 96, output / "favicon-96x96.png")
    resize_square(ICON_SOURCE, 180, output / "apple-touch-icon.png")
    resize_square(ICON_SOURCE, 500, output / "logo.png")
    resize_square(ICON_SOURCE, 192, output / "web-app-manifest-192x192.png")
    icon_512 = resize_square(ICON_SOURCE, 512, output / "web-app-manifest-512x512.png")

    ico_path = output / "favicon.ico"
    icon_512.save(
        ico_path,
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)],
    )
    print("wrote", ico_path)
    copy_asset(FAVICON_SVG_SOURCE, output / "favicon.svg")

    # Splash screens use the approved colour/reverse symbol artwork.
    resize_to_width(SYMBOL_SOURCE, 500, output / "splash.png")
    resize_to_width(SYMBOL_REVERSE_SOURCE, 500, output / "splash-dark.png")

    # Reusable lockups for branded UI surfaces and downstream integrations.
    brand_output = output / "brand"
    resize_to_width(SYMBOL_SOURCE, 512, brand_output / "devagent-mark.png")
    copy_asset(COMPACT_SOURCE, brand_output / "devagent-compact.png")
    copy_asset(COMPACT_REVERSE_SOURCE, brand_output / "devagent-compact-reverse.png")
    copy_asset(HORIZONTAL_SOURCE, brand_output / "devagent-horizontal.png")


def main() -> None:
    require_sources()
    for output in OUTPUTS:
        generate_assets(output)

    # SvelteKit also exposes this root fallback before the backend starts.
    if len(sys.argv) == 1:
        resize_square(ICON_SOURCE, 512, Path("static/favicon.png"))


if __name__ == "__main__":
    main()
