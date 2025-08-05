### Excluded Developer-Only/Destructive Routes from E2E Testing

The following routes are **not covered by E2E tests** because they are intended exclusively for development, debugging, or administrative use. They are not part of any user workflow and may be destructive or expose sensitive internals.

| Route                        | Description                                      | Reason for Exclusion         |
|------------------------------|--------------------------------------------------|-----------------------------|
| `/delete_testing_range`      | Deletes test data from the database              | Dev-only, destructive       |
| `/js_diagnostic_log`         | Accepts JS diagnostics from frontend             | Dev-only, not user-facing   |
| `/diagnostics`               | Shows backend diagnostics and runtime info       | Dev-only, not user-facing   |
| `/show_log_file`             | Displays backend log file                        | Dev-only, not user-facing   |
| `/java_script_diagnostic_test` | JS diagnostics test page                       | Dev-only, not user-facing   |
| ...                          | ...                                              | ...                         |

These endpoints may be tested manually or with isolated unit/integration tests in a disposable environment. They are not part of the production user workflow and are excluded from automated E2E coverage by design.