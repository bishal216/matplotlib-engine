import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_fig_ax():
    """Shared fixture that provides a fully mocked matplotlib fig and ax.
    Prevents any actual rendering during tests."""
    fig = MagicMock()
    ax  = MagicMock()
    ax.figure = fig
    fig.canvas.mpl_connect.return_value = 1   # fake connection id
    fig.canvas.mpl_disconnect.return_value = None
    fig.canvas.draw_idle.return_value = None
    return fig, ax
