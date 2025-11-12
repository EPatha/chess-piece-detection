"""Quick import/test script for this project.

Run inside your activated `.venv` to verify dependencies.

Usage:
    source .venv/bin/activate
    python3 test_imports.py

It prints which imports succeeded and shows the Python executable used.
"""
import sys
from importlib import import_module

print('Python executable:', sys.executable)

modules = [
    ('threading', 'threading (stdlib)'),
    ('io', 'io (stdlib)'),
    ('cv2', 'opencv-python (cv2)'),
    ('numpy', 'numpy'),
    ('PIL', 'Pillow (PIL)'),
    ('flask', 'Flask'),
    ('requests', 'requests'),
    ('torch', 'torch'),
    ('ultralytics', 'ultralytics'),
]

results = []
for name, pretty in modules:
    try:
        mod = import_module(name)
        version = getattr(mod, '__version__', None)
        results.append((pretty, True, version))
    except Exception as e:
        results.append((pretty, False, str(e)))

for pretty, ok, info in results:
    if ok:
        print(f'[OK]   {pretty}  version={info}')
    else:
        print(f'[FAIL] {pretty}  error={info}')

print('\nIf something fails, run:')
print('  source .venv/bin/activate')
print('  pip install --upgrade pip setuptools wheel')
print('  pip install -r requirements.txt')
