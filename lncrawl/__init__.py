#!/usr/bin/env python3

def main():
    # For executable bundles
    try:
        import multiprocessing
        multiprocessing.freeze_support()
    except Exception:
        pass

    from .app import app
    app()


if __name__ == "__main__":
    main()
