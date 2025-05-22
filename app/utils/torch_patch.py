# app/utils/torch_patch.py

import sys

# Torch might not be installed yet — don't crash
try:
    import torch

    # Remove the faulty attribute that causes Streamlit crash
    if hasattr(torch, "classes") and "__path__" in dir(torch.classes):
        try:
            del torch.classes.__path__
        except Exception:
            pass

    # Fully remove torch.classes if needed
    if hasattr(torch, "classes"):
        torch.classes = None
        if "torch.classes" in sys.modules:
            del sys.modules["torch.classes"]

except ImportError:
    pass
