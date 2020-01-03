from app import app
from livereload import Server
import sys


def _init_asyncio_patch():
    """
    Select compatible event loop for Tornado 5+.
    As of Python 3.8, the default event loop on Windows is `proactor`,
    however Tornado requires the old default "selector" event loop.
    As Tornado has decided to leave this to users to set, MkDocs needs
    to set it. See https://github.com/tornadoweb/tornado/issues/2608.

    Taken from: https://github.com/mkdocs/mkdocs/commit/cf2b136d4257787c0de51eba2d9e30ded5245b31
    """
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        import asyncio

        try:
            from asyncio import WindowsSelectorEventLoopPolicy
        except ImportError:
            pass  # Can't assign a policy which doesn't exist.
        else:
            if not isinstance(
                asyncio.get_event_loop_policy(), WindowsSelectorEventLoopPolicy
            ):
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


if __name__ == "__main__":
    _init_asyncio_patch()

    server = Server(app.wsgi_app)
    server.serve(host="0.0.0.0", port=5000)
