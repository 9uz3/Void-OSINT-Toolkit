"""Plugin discovery — stub."""
import os
from . import constants as C


def discover_plugins():
    custom_dir = C.CUSTOM_TOOLS_DIR
    if not os.path.isdir(custom_dir):
        return []
    plugins = []
    for fname in sorted(os.listdir(custom_dir)):
        if fname.endswith(".py") and fname != "__init__.py":
            path = os.path.join(custom_dir, fname)
            label = fname[:-3].replace("-", " ").replace("_", " ").title()
            plugins.append((f"{len(plugins)+1:02d}", label, path))
    return plugins
