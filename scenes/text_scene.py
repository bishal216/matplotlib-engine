import os
import matplotlib.pyplot as plt

def text_scene(ax, scene, settings):
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Load background
    location_key = scene.get('location')
    background_path = settings.get(location_key, {}).get('background')
    if background_path and os.path.exists(background_path):
        img = plt.imread(background_path)
        ax.imshow(img, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    # Title
    title = scene.get('title', '')
    ax.text(0.5, 0.85, title,
            fontsize=24, fontweight='bold', ha='center', va='center', color='white',
            bbox=dict(facecolor='black', alpha=0.6, pad=8), zorder=1)

    # Content lines
    content_lines = scene.get('content', [])
    for i, line in enumerate(content_lines):
        y = 0.6 - i * 0.07  # adjust line spacing
        ax.text(0.5, y, line,
                fontsize=14, ha='center', va='center', color='white',
                bbox=dict(facecolor='black', alpha=0.4, pad=4), wrap=True, zorder=1)

    # Optional: instructions at bottom
    ax.text(0.5, 0.08, "Press space to continue...",
            fontsize=10, ha='center', va='center', color='#cccccc', zorder=1)

    plt.draw()
    plt.pause(2)