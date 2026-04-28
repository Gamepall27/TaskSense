"""Einstiegspunkt für TaskSense Lite."""
import os

os.environ["TASKSENSE_EDITION"] = "lite"

from main import main


if __name__ == "__main__":
    main()
