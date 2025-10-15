#!/usr/bin/env python3

def main():
    # For executable bundles
    try:
        import multiprocessing
        multiprocessing.freeze_support()
    except Exception:
        pass

    # For encoding
    try:
        import sys
        reconfigure = getattr(sys.stdout, 'reconfigure', None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    except Exception:
        pass

    # start the app
    from .app import app
    app()


if __name__ == "__main__":
    main()
