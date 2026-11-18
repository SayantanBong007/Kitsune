# Evaluation repositories

Code used by Kitsune's quality evaluations. Nothing here is part of Kitsune itself.

| Folder | What | Used by |
|---|---|---|
| `shop/`, `notes/`, `ledger/` | Small fixtures written for Kitsune (Python, TypeScript/JS, Go) with known answers | `eval/run_eval.py` |
| `gson/` | Google Gson (fetched, not committed) | `eval/eval_v2.py gson` |
| `spring_petclinic/` | Spring PetClinic (fetched, not committed) | `eval/eval_v2.py petclinic` |

## Third-party sources (fetched, not committed)

`gson/` and `spring_petclinic/` are not stored in this repository. Fetch them at the
pinned commits before running benchmark v2:

```bash
python kitsune/eval/fetch_external.py
```

| Folder | Upstream | Commit |
|---|---|---|
| `gson/` | https://github.com/google/gson | `828cbe0d7c5ab224c9bf441914ee391677196c0f` |
| `spring_petclinic/` | https://github.com/spring-projects/spring-petclinic | `500158f732419217507c7656904b8e6aa1bcc0d6` |

Both are Apache License 2.0 projects. Both folders are git-ignored.

**Reproducing the published Gson numbers exactly:** the Gson benchmark was measured with
the 33 Java files that Gson's own Maven build generates (protobuf test classes under
`proto/target/generated-test-sources/`). A fresh clone doesn't have them; run
`mvn -q generate-test-sources` inside `gson/proto` to create them before indexing.
