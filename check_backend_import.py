import pathlib
import sys

root = pathlib.Path(__file__).parent
backend = root / 'backend'
sys.path.insert(0, str(backend))
sys.path.insert(0, str(root))

try:
    from app.main import app
    print('backend import ok')
except Exception as exc:
    print(type(exc).__name__ + ': ' + str(exc))
    raise
