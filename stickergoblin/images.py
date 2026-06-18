try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
    Image = None  # type: ignore[assignment,misc]
    ImageTk = None  # type: ignore[assignment,misc]
