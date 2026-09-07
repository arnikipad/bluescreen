"""
BlueScreen Trigger v6.0 "Autumn" (2026) - Safer release metadata and CLI wrapper

This module provides a backwards-compatible wrapper around BlueScreenTriggerV5
and exposes the new v6.0 "Autumn" entry point. For safety the executable
requires an explicit --enable-trigger flag and an environment variable
BLUESCREEN_ENABLE=1 to perform any non-dry-run trigger. By default the
release remains in dry-run mode.

Release naming notes:
- Meteorological autumn 2026 begins on 2026-09-01
- Astronomical autumn (autumnal equinox) 2026 begins on 2026-09-22

References:
- https://www.metoffice.gov.uk/blog/2026/when-does-autumn-start
- https://www.timeanddate.com/calendar/autumnal-equinox.html
- https://www.almanac.com/content/first-day-fall-autumnal-equinox

This file intentionally avoids changing the core trigger implementation;
it adds an additional safety gate and updates the package entry point to
reference v6 so the package can be released with an explicit, well-documented
guard for deliberate use only by authorized operators.
"""

from __future__ import annotations
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from bluescreen_v5 import BlueScreenTriggerV5


__version__ = "6.0.0-autumn"
RELEASE_NAME = "Autumn"
RELEASE_YEAR = 2026


class BlueScreenTriggerV6:
    """Wrapper for v5 with Autumn release metadata and extra safety checks."""

    def __init__(self, dry_run: bool = True):
        self.release = f"v6.0 {RELEASE_NAME} ({RELEASE_YEAR})"
        self.trigger = BlueScreenTriggerV5(dry_run=dry_run)
        self.logger = logging.getLogger("BlueScreenV6")
        self.logger.setLevel(logging.DEBUG)

    def get_release_info(self):
        return {
            "version": "v6.0",
            "name": RELEASE_NAME,
            "year": RELEASE_YEAR,
            "timestamp": datetime.now().isoformat()
        }

    def execute(self, enable_trigger: bool = False) -> bool:
        """Execute the wrapped trigger. A second safety gate is required to
        perform any non-dry-run action: both enable_trigger=True and
        environment variable BLUESCREEN_ENABLE=1 must be present.
        """
        if not enable_trigger:
            self.logger.warning("Enable flag not provided: running in dry-run mode")
            self.trigger.dry_run = True
            return self.trigger.execute()

        # Safety gate: require explicit environment variable to allow real trigger
        if os.environ.get("BLUESCREEN_ENABLE") != "1":
            self.logger.error("BLUESCREEN_ENABLE not set to '1' - aborting real trigger")
            self.trigger.dry_run = True
            return self.trigger.execute()

        # If both checks passed, perform the trigger (still checks platform inside v5)
        self.trigger.dry_run = False
        return self.trigger.execute()


def main():
    parser = argparse.ArgumentParser(description="BlueScreen Trigger v6.0 Autumn - safer entry point")

    parser.add_argument("--dry-run", action="store_true", help="Run without actual system effects (default)")
    parser.add_argument("--enable-trigger", action="store_true",
                        help="Allow a real trigger if BLUESCREEN_ENABLE=1 is set in the environment")
    parser.add_argument("--collect", action="store_true", help="Collect system metrics (dry-run safe)")
    parser.add_argument("--train", action="store_true", help="Train ML models (dry-run safe)")
    parser.add_argument("--analyze", action="store_true", help="Analyze metrics (dry-run safe)")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations (dry-run safe)")
    parser.add_argument("--report", action="store_true", help="Generate analytics report (dry-run safe)")
    parser.add_argument("--trigger", action="store_true", help="Execute trigger (requires --enable-trigger and BLUESCREEN_ENABLE=1)")
    parser.add_argument("--hours", type=int, default=24, help="Hours of historical data")

    args = parser.parse_args()

    # Default to dry-run unless the user explicitly requests otherwise
    effective_dry_run = True if args.dry_run or not args.trigger else False

    v6 = BlueScreenTriggerV6(dry_run=effective_dry_run)

    if args.collect:
        metrics = v6.trigger.metrics_collector.collect_metrics()
        print(json.dumps(metrics.__dict__, indent=2))
        return

    if args.train:
        ok = v6.trigger.train_models(args.hours)
        print("Models trained" if ok else "Training failed")
        return

    if args.analyze:
        analysis = v6.trigger.collect_and_analyze()
        print(json.dumps(analysis, indent=2))
        return

    if args.visualize:
        files = v6.trigger.generate_visualizations()
        print("Generated files:")
        for f in files:
            print(f)
        return

    if args.report:
        report = v6.trigger.generate_analytics_report()
        print(report)
        return

    if args.trigger:
        # require both --enable-trigger and environment variable
        if not args.enable_trigger:
            print("--enable-trigger required to perform a real trigger. Running in dry-run.")
            v6.trigger.dry_run = True
            v6.trigger.execute()
            return

        result = v6.execute(enable_trigger=True)
        print("Trigger executed" if result else "Trigger failed or aborted")
        return

    # If no specific action, show release info
    print(json.dumps(v6.get_release_info(), indent=2))


if __name__ == "__main__":
    main()
