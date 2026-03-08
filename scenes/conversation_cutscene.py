import os
import logging

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

logger = logging.getLogger(__name__)

# ── Layout constants ───────────────────────────────────────────────────────────
SPRITE_LEFT_EXTENT = [0.05, 0.35, 0.55, 0.95]  # [x0, x1, y0, y1]
SPRITE_RIGHT_EXTENT = [0.65, 0.95, 0.55, 0.95]

DIM_ALPHA = 0.3
DIALOGUE_Y = 0.10
NAME_Y = 0.95
DIALOGUE_FONT = 16
NAME_FONT = 12
PAUSE_INTERVAL = 0.05  # seconds between event polls


def _load_image(path: str | None):
    """Load an image from disk, returning None if missing or invalid."""
    if not path or not os.path.exists(path):
        if path:
            logger.warning("Image not found: %s", path)
        return None
    try:
        return mpimg.imread(path)
    except Exception as e:
        logger.error("Failed to load image %s: %s", path, e)
        return None


def _cache_assets(bg_img: str | None, characters: dict) -> tuple:
    """
    Load background and all character sprites once upfront.
    Returns (bg_array | None, {char_name: image_array | None})
    """
    bg = _load_image(bg_img)

    sprite_cache = {}
    for name, info in characters.items():
        sprite_cache[name] = _load_image(info.get("sprite"))

    return bg, sprite_cache


def conversation_cutscene(
    ax,
    bg_img: str | None = None,
    conversation: list | None = None,
    characters: dict | None = None,
) -> None:
    if not conversation:
        logger.warning("conversation_cutscene called with empty conversation")
        return

    characters = characters or {}
    fig = ax.figure

    # ── Cache all assets upfront — not per line ────────────────────────────────
    bg, sprite_cache = _cache_assets(bg_img, characters)

    # ── Event handling ─────────────────────────────────────────────────────────
    continue_flag = {"clicked": False}

    def on_click(event):
        continue_flag["clicked"] = True

    def on_key(event):
        if event.key in (" ", "space"):
            continue_flag["clicked"] = True

    cid_click = fig.canvas.mpl_connect("button_press_event", on_click)
    cid_key = fig.canvas.mpl_connect("key_press_event", on_key)

    try:
        for line in conversation:
            continue_flag["clicked"] = False

            char = line.get("character", "")
            char_info = characters.get(char, {})
            side = char_info.get("side")
            text = line.get("text", "")

            _render_line(ax, fig, bg, sprite_cache.get(char), char, text, side)

            # Wait for click or spacebar
            while not continue_flag["clicked"]:
                plt.pause(PAUSE_INTERVAL)

    finally:
        # Always disconnect listeners — even if an exception occurs
        fig.canvas.mpl_disconnect(cid_click)
        fig.canvas.mpl_disconnect(cid_key)

    plt.draw()


def _render_line(ax, fig, bg, sprite, char: str, text: str, side: str | None) -> None:
    """Clear and redraw the scene for a single dialogue line."""
    ax.clear()
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Background
    if bg is not None:
        ax.imshow(bg, extent=[0, 1, 0, 1], aspect="auto", zorder=0)

    # Character sprite
    if sprite is not None and side in ("left", "right"):
        extent = SPRITE_LEFT_EXTENT if side == "left" else SPRITE_RIGHT_EXTENT
        ax.imshow(
            sprite, extent=extent, aspect="auto", interpolation="bilinear", zorder=1
        )

    # Dim the inactive side
    if side == "left":
        ax.fill_betweenx([0, 1], 0.65, 1.0, color="black", alpha=DIM_ALPHA, zorder=1.5)
    elif side == "right":
        ax.fill_betweenx([0, 1], 0.0, 0.35, color="black", alpha=DIM_ALPHA, zorder=1.5)

    # Character name badge
    if side in ("left", "right"):
        name_x = 0.05 if side == "left" else 0.95
        name_ha = "left" if side == "left" else "right"
        ax.text(
            name_x,
            NAME_Y,
            char,
            ha=name_ha,
            va="top",
            fontsize=NAME_FONT,
            color="white",
            weight="bold",
            bbox=dict(facecolor="black", alpha=0.5, pad=3),
            zorder=2,
        )

    # Dialogue box
    ax.text(
        0.5,
        DIALOGUE_Y,
        f"{char}: {text}",
        ha="center",
        va="center",
        fontsize=DIALOGUE_FONT,
        wrap=True,
        bbox=dict(facecolor="white", alpha=0.85, boxstyle="round,pad=0.7"),
        zorder=3,
    )

    fig.canvas.draw_idle()
