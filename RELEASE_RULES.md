# Release rules (agreed with the platform and security teams)

1. **Production needs a person's approval.** The `prd` environment in Azure DevOps already has an
   approval check (the release manager). It only applies to a `deployment` job that targets that
   environment. Production is deployed only after TST deployed successfully.
2. **No secrets in the repository.** Client secrets live in the Azure Key Vault `kv-storerequests`.
   The pipeline reads them at run time. The secret for each environment's service principal is named
   `pp-secret-dev`, `pp-secret-tst` and `pp-secret-prd`. The service connection to read the vault is
   called `azure-keyvault-reader`.
3. **Each environment has its own settings.** Environment variables and connection references are set
   with the deployment settings file of that environment (`settings/<env>.json`). The correct values
   are in `ENVIRONMENTS.md`.
