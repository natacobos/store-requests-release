# Fix a Power Platform release pipeline before it reaches production

Our team deploys the "Store Requests" Power Platform solution with an Azure DevOps pipeline and the
Power Platform CLI: build, then DEV, TST and PRD. A review found three problems that break our release
rules. Your job is to fix them in the files. You don't run the pipeline and you don't need Azure.

You may use your usual AI tool; we will watch how you use it. Please think out loud.

## Files

- `RELEASE_RULES.md`: the three rules. Read it first.
- `pipelines/release.yml`: the pipeline.
- `settings/dev.json`, `settings/tst.json`, `settings/prd.json`: the settings of each environment.
- `ENVIRONMENTS.md`: the correct values per environment.

## Tasks: 15 minutes in total (any order)

1. **Approval before production (about 5 minutes).** Today PRD can deploy without anyone approving
   it, and even when TST failed. Fix the PRD stage so rule 1 applies.
2. **Secrets (about 6 minutes).** A client secret is written in the pipeline. Remove it and make each
   environment sign in with its own secret from Key Vault (rule 2).
3. **TST settings (about 4 minutes).** TST points to the production service desk and uses another
   environment's connection. Fix `settings/tst.json` (rule 3).

If you are still on one task two minutes after its time, move on to the next one.

At 15 minutes we stop. Then run (Python 3, nothing to install):

```
python3 check/check.py
```

Do not edit the `check` folder.
