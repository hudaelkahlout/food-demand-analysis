"""Validate installed upstream skills using synthetic inputs only; no project analysis."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"exploratory-data-analysis", "scikit-learn"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-python", help="Optional isolated Python with scikit-learn installed")
    parser.add_argument("--phase3-snapshot", action="store_true",
                        help="Also require Phase 4 artifacts to be absent (historical Phase 3 boundary)")
    args = parser.parse_args()
    skills = ROOT / ".agents/skills"
    assert {p.name for p in skills.iterdir() if p.is_dir()} == NAMES
    source = json.loads((ROOT / "docs/phase3_skill_sources.json").read_text(encoding="utf-8"))
    verified = 0
    for entry in source["files"]:
        relative = Path(entry["path"])
        if relative.parts[0] != "skills":
            continue
        local = skills / Path(*relative.parts[1:])
        payload = local.read_bytes()
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"], local
        assert hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest() == entry["git_blob"]
        verified += 1
    script_count = 0
    link_count = 0
    for name in sorted(NAMES):
        directory = skills / name
        text = (directory / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert re.search(rf"^name: {re.escape(name)}$", text, re.M)
        assert re.search(r"^description: .+", text, re.M)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            assert (directory / target.split("#")[0]).is_file(), target
            link_count += 1
        for script in directory.rglob("*.py"):
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            script_count += 1
    # Exercise the installed EDA core on a temporary, synthetic fixture.
    scripts = skills / "exploratory-data-analysis/scripts"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(prefix="food-demand-phase3-smoke-") as temporary:
        fixture_root = Path(temporary).resolve()
        fixture = fixture_root / "fixture.csv"
        fixture.write_text("week,value,group\n1,10,A\n2,,A\n3,30,B\n", encoding="utf-8")
        original = fixture.read_bytes()

        def run(script, *arguments, expected=0):
            result = subprocess.run([sys.executable, str(scripts / script), *map(str, arguments)],
                                    capture_output=True, text=True, env=env)
            assert result.returncode == expected, result.stderr
            return json.loads(result.stdout) if expected == 0 else result.stderr

        manifest = run("capability_manifest.py", "inspect", "fixture.csv", "--root", fixture_root)
        assert manifest["capability"]["tier"] == "automated_core"
        profile = run("tabular_profile.py", "fixture.csv", "--root", fixture_root)
        analysis = profile["analysis"]
        assert analysis["rows_scanned"] == 3, analysis
        assert not analysis["row_limit_reached"], analysis
        assert not profile["security"]["raw_values_and_full_paths_emitted"]
        prefix = run("tabular_profile.py", "fixture.csv", "--root", fixture_root, "--max-rows", "2")
        assert prefix["analysis"]["rows_scanned"] == 2
        assert prefix["analysis"]["row_limit_reached"]
        assert "path escapes" in run("capability_manifest.py", "inspect", ROOT / "README.md",
                                     "--root", fixture_root, expected=2)
        assert fixture.read_bytes() == original
    # Use the ML guide as procedural knowledge without running demand models.
    ml = skills / "scikit-learn"
    evaluation = (ml / "references/model_evaluation.md").read_text(encoding="utf-8")
    composition = (ml / "references/pipelines_and_composition.md").read_text(encoding="utf-8")
    supervised = (ml / "references/supervised_learning.md").read_text(encoding="utf-8")
    for needle, text in [("TimeSeriesSplit", evaluation), ("mean_absolute_error", evaluation),
                         ("ColumnTransformer", composition), ("Pipeline", composition),
                         ("LinearRegression", supervised), ("RandomForestRegressor", supervised)]:
        assert needle in text, needle
    runtime = "not run; guidance and reference availability verified"
    if args.runtime_python:
        code = """
import json
import numpy as np
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
assert sklearn.__version__ == '1.9.1'
for left, right in TimeSeriesSplit(n_splits=2).split(np.arange(6)):
    assert max(left) < min(right)
pipeline = Pipeline([('scale', StandardScaler()), ('regressor', LinearRegression())])
forest = RandomForestRegressor(random_state=42)
assert mean_absolute_error([1, 3], [2, 2]) == 1
print(json.dumps({'scikit_learn': sklearn.__version__, 'api_imports': 'passed',
                  'synthetic_split_and_mae': 'passed', 'model_fitting': 'not performed'}))
"""
        result = subprocess.run([args.runtime_python, "-c", code], capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        runtime = json.loads(result.stdout)
    inventory = (ROOT / "docs/data_inventory.md").read_text(encoding="utf-8")
    raw = list((ROOT / "data/raw").glob("*.csv"))
    assert len(raw) == 4
    for path in raw:
        assert hashlib.sha256(path.read_bytes()).hexdigest() in inventory, path.name
    custom_present = [name for name in ("promotion-impact-analysis", "client-insight-reporting")
                      if (ROOT / ".github/skills" / name / "SKILL.md").exists()]
    if args.phase3_snapshot:
        assert not custom_present
        assert not (ROOT / "docs/skills_testing.md").exists()
    result = {"status": "passed", "selected_skills": sorted(NAMES), "upstream_files_verified": verified,
              "python_scripts_syntax_checked": script_count, "skill_local_links_checked": link_count,
              "eda_synthetic_checks": ["manifest", "three-row profile", "two-row cap disclosed",
                                       "out-of-root input rejected", "fixture unchanged"],
              "scikit_learn_guidance_check": "passed", "scikit_learn_runtime_check": runtime,
              "raw_dataset_hashes": "all four match Phase 1",
              "phase4_custom_skills": "absent" if not custom_present else "present; outside Phase 3 validation scope"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
