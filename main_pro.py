"""Einstiegspunkt für TaskSense Pro."""
import os

os.environ["TASKSENSE_EDITION"] = "pro"

from main import main


if __name__ == "__main__":
    main()
