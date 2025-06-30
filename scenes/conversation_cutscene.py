import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def conversation_cutscene(ax, bg_img: str = None, conversation=None, CHARACTERS=None):
    fig = ax.figure

    # Load background image if provided
    bg = None
    if bg_img and os.path.exists(bg_img):
        bg = mpimg.imread(bg_img)

    continue_flag = {'clicked': False}

    def on_click(event):
        continue_flag['clicked'] = True

    def on_key(event):
        if event.key == ' ':
            continue_flag['clicked'] = True

    # Connect event listeners
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('key_press_event', on_key)

    for line in conversation:
        continue_flag['clicked'] = False

        ax.clear()
        ax.axis('off')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Draw background full screen
        if bg is not None:
            ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

        # Get character info
        char = line['character']
        char_info = CHARACTERS.get(char, {"sprite": None, "side": None})
        sprite_path = char_info.get("sprite", None)
        side = char_info.get("side", None)

        # Sprite positioning
        if side == "left":
            sprite_extent = [0.05, 0.35, 0.55, 0.95]
        elif side == "right":
            sprite_extent = [0.65, 0.95, 0.55, 0.95]
        else:
            sprite_extent = None

        # Draw character sprite
        if sprite_path and os.path.exists(sprite_path) and sprite_extent:
            sprite_img = mpimg.imread(sprite_path)
            ax.imshow(sprite_img, extent=sprite_extent, aspect='auto', interpolation='bilinear', zorder=1)

        # Dim the opposite side
        if side == "left":
            ax.fill_betweenx([0, 1], 0.65, 1, color='black', alpha=0.3, zorder=1.5)
        elif side == "right":
            ax.fill_betweenx([0, 1], 0, 0.35, color='black', alpha=0.3, zorder=1.5)

        # Draw character name at top
        if side in {"left", "right"}:
            name_x = 0.05 if side == "left" else 0.95
            ax.text(name_x, 0.95, char, ha='left' if side == "left" else 'right',
                    va='top', fontsize=12, color='white', weight='bold',
                    bbox=dict(facecolor='black', alpha=0.5, pad=3),
                    zorder=2)

        # Draw dialogue box at bottom center
        ax.text(0.5, 0.1, f"{char}: {line['text']}",
                ha='center', va='center', fontsize=16, wrap=True,
                bbox=dict(facecolor='white', alpha=0.85, boxstyle='round,pad=0.7'),
                zorder=3)

        fig.canvas.draw_idle()

        while not continue_flag['clicked']:
            plt.pause(0.1)

    plt.draw()

