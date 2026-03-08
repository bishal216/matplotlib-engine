import os
import logging

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

logger = logging.getLogger(__name__)

# ── Layout constants ───────────────────────────────────────────────────────────
TITLE_Y         = 0.88
TITLE_FONT      = 20
CONTENT_START_Y = 0.76
CONTENT_STEP_Y  = 0.055
CONTENT_MIN_Y   = 0.14    # lines won't render below this threshold
CONTENT_FONT    = 12
PROMPT_Y        = 0.05
PROMPT_FONT     = 9
PAUSE_INTERVAL  = 0.05    # seconds between event polls


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


def text_scene(ax, scene: dict, settings: dict) -> None:
    fig = ax.figure

    # ── Clear and configure axes ───────────────────────────────────────────────
    ax.clear()
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── Background ─────────────────────────────────────────────────────────────
    location_key    = scene.get("location")
    background_path = settings.get(location_key, {}).get("background")
    bg              = _load_image(background_path)

    if bg is not None:
        ax.imshow(bg, extent=[0, 1, 0, 1], aspect="auto", zorder=0)

    # ── Title ──────────────────────────────────────────────────────────────────
    title = scene.get("title", "")
    if title:
        ax.text(
            0.5, TITLE_Y, title,
            fontsize=TITLE_FONT, fontweight="bold",
            ha="center", va="center", color="white",
            bbox=dict(facecolor="black", alpha=0.6, pad=8),
            zorder=1,
        )

    # ── Content lines ──────────────────────────────────────────────────────────
    content_lines = scene.get("content", [])
    for i, line in enumerate(content_lines):
        y = CONTENT_START_Y - i * CONTENT_STEP_Y

        if y < CONTENT_MIN_Y:
            logger.warning(
                "text_scene: content truncated — line %d would render below y=%.2f", i, CONTENT_MIN_Y
            )
            break

        ax.text(
            0.5, y, line,
            fontsize=CONTENT_FONT,
            ha="center", va="center", color="white", wrap=True,
            bbox=dict(facecolor="black", alpha=0.4, pad=4),
            zorder=1,
        )

    # ── Prompt ─────────────────────────────────────────────────────────────────
    ax.text(
        0.5, PROMPT_Y, "Press space or click to continue...",
        fontsize=PROMPT_FONT, ha="center", va="center", color="#cccccc",
        zorder=1,
    )

    fig.canvas.draw_idle()

    # ── Wait for input ─────────────────────────────────────────────────────────
    continue_flag = {"clicked": False}

    def on_click(event):
        continue_flag["clicked"] = True

    def on_key(event):
        if event.key in (" ", "space"):
            continue_flag["clicked"] = True

    cid_click = fig.canvas.mpl_connect("button_press_event", on_click)
    cid_key   = fig.canvas.mpl_connect("key_press_event",   on_key)

    try:
        while not continue_flag["clicked"]:
            plt.pause(PAUSE_INTERVAL)
    finally:
        fig.canvas.mpl_disconnect(cid_click)
        fig.canvas.mpl_disconnect(cid_key)