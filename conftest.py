import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")
