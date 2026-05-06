"""Run the full clinical survival analysis pipeline."""

from __future__ import annotations

import importlib
import time


PIPELINE_STEPS = [
    ("Prepare data", "prepare_data"),
    ("Kaplan-Meier and log-rank", "run_kaplan_meier"),
    ("Cox proportional hazards", "train_cox_model"),
    ("Random Survival Forest", "train_random_survival_forest"),
    ("Summary report", "evaluate_models"),
]


def main() -> None:
    started = time.time()

    for label, module_name in PIPELINE_STEPS:
        step_started = time.time()
        print(f"\n== {label} ==")
        module = importlib.import_module(module_name)
        module.main()
        print(f"Completed {label} in {time.time() - step_started:.1f}s")

    print(f"\nPipeline complete in {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
