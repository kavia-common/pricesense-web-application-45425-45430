import importlib
import sys

try:
    mod = importlib.import_module("src.api.main")
    app = getattr(mod, "app", None)
    if app is None:
        print("App not found on module.")
        sys.exit(2)
    print("App imported successfully. Routes:", len(app.routes))
    sys.exit(0)
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
