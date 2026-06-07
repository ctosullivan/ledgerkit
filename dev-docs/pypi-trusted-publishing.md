# PyPI Trusted Publishing Setup

LedgerKit uses PyPI's Trusted Publishing (OIDC) for releases — no API token
is stored in GitHub Secrets.

## One-time setup: Test PyPI

1. Log in to https://test.pypi.org
2. Go to Account → Publishing → **Add a new pending publisher**
3. Fill in:
   - PyPI project name: `ledgerkit`
   - Owner: `ctosullivan`
   - Repository name: `ledgerkit`
   - Workflow filename: `publish.yml`
   - Environment name: `test-pypi`

## One-time setup: PyPI (production)

Repeat the above at https://pypi.org with environment name `pypi`.

## One-time setup: GitHub environments

In the GitHub repo settings → Environments:

1. Create environment `test-pypi` (no protection rules needed)
2. Create environment `pypi` — add a **Required reviewers** protection rule
   (yourself) so production releases require manual approval

## Publishing a release

### To Test PyPI (manual trigger)
1. Go to Actions → Publish to PyPI → Run workflow
2. Select target: `testpypi`
3. Click Run workflow

### To PyPI (on version tag)
```bash
git tag v0.2.0
git push origin v0.2.0
```
The publish workflow fires automatically, targets the `pypi` environment, and
waits for reviewer approval before publishing.

## Verifying a Test PyPI release

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ledgerkit
```
