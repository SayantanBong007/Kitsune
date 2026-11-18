"""
Fetch the public code used by Kitsune's evaluations, at pinned commits:

- the microservice systems for eval/run_system_eval.py  -> eval/external/
- Gson and Spring PetClinic for eval/eval_v2.py          -> eval/repos/gson, eval/repos/spring_petclinic

All of these folders are git-ignored, so results are reproducible and the
Kitsune repository stays small.

    python kitsune/eval/fetch_external.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
EXTERNAL = EVAL_DIR / "external"
REPOS_DIR = EVAL_DIR / "repos"

# Benchmark v2 (eval/eval_v2.py): (folder under eval/repos, repository, commit)
V2_REPOS = [
    ("gson", "https://github.com/google/gson.git", "828cbe0d7c5ab224c9bf441914ee391677196c0f"),
    ("spring_petclinic", "https://github.com/spring-projects/spring-petclinic.git", "500158f732419217507c7656904b8e6aa1bcc0d6"),
]

# (folder, repository, commit)
REPOS = [
    ("sockshop/front-end", "https://github.com/microservices-demo/front-end.git", "52dee65"),
    ("sockshop/catalogue", "https://github.com/microservices-demo/catalogue.git", "925e08e"),
    ("sockshop/carts", "https://github.com/microservices-demo/carts.git", "f4e8005"),
    ("sockshop/orders", "https://github.com/microservices-demo/orders.git", "546a10c"),
    ("sockshop/payment", "https://github.com/microservices-demo/payment.git", "384e334"),
    ("sockshop/user", "https://github.com/microservices-demo/user.git", "e1a79e7"),
    ("sockshop/shipping", "https://github.com/microservices-demo/shipping.git", "9c0fbfa"),
    ("sockshop/queue-master", "https://github.com/microservices-demo/queue-master.git", "7dc3372"),
    ("boutique", "https://github.com/GoogleCloudPlatform/microservices-demo.git", "38e7348"),
    ("petclinic-ms", "https://github.com/spring-petclinic/spring-petclinic-microservices.git", "e8b747a"),
    ("robot-shop", "https://github.com/instana/robot-shop.git", "55292e2"),
    ("train-ticket", "https://github.com/FudanSELab/train-ticket.git", "313886e"),
    ("piggymetrics", "https://github.com/sqshq/piggymetrics.git", "6bb2cf9"),
]


def run(*cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def fetch(base: Path, folder: str, url: str, commit: str):
    dest = base / folder
    if dest.exists() and not (dest / ".git").exists():
        # A plain copy (for example from an older checkout of this repo): leave it alone.
        print(f"{folder:28} already present (not a git clone), skipped")
        return
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"cloning {url} -> {dest}")
        run("git", "clone", "--quiet", "--filter=blob:none", url, str(dest))
    run("git", "-c", "advice.detachedHead=false", "checkout", "--quiet", commit, cwd=dest)
    print(f"{folder:28} @ {commit[:7]}")


def main():
    for folder, url, commit in REPOS:
        fetch(EXTERNAL, folder, url, commit)
    for folder, url, commit in V2_REPOS:
        fetch(REPOS_DIR, folder, url, commit)


if __name__ == "__main__":
    sys.exit(main())
