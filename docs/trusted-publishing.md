# Publishing a verified distribution to PyPI

Pull requests build and test the proposed commit. Production publication requires a separate manual run from `main`, an annotated release tag, and approval in the GitHub `pypi` environment. The same Python distribution includes the CLI and the canonical skill. [Release workflow](../.github/workflows/release.yml) · [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

## One-time owner configuration

1. In this repository's **Settings → Environments**, create `pypi`. Under **Deployment protection rules**, enable **Required reviewers** and select a maintainer. Under **Deployment branches and tags**, choose **Selected branches and tags** and add a single **Branch** rule for `main`. Save the rules before enabling the PyPI trust relationship. If you enable **Prevent self-review**, arrange a second reviewer who can approve deployments. [Repository environments](https://github.com/hnt119/wechat-sticker-publisher/settings/environments) · [GitHub environment settings](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
2. Sign in to the intended PyPI owner account. Open **Account settings → Publishing**, select **GitHub** and add a pending publisher using the values below. A pending publisher does not reserve the name. PyPI creates the project on a successful first upload if it accepts the name. For a project you already own, add the publisher through that project's **Manage → Publishing**. [PyPI account publishing settings](https://pypi.org/manage/account/publishing/) · [First-time publisher setup](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) · [Existing project setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)

| PyPI field | Value |
| --- | --- |
| PyPI project name | `wechat-sticker-publisher` |
| Owner | `hnt119` |
| Repository name | `wechat-sticker-publisher` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

Keep ownership of the PyPI name and final publication approval as separate checks. Recheck the [public project index](https://pypi.org/project/wechat-sticker-publisher/) before a first upload. If a project with a different owner has appeared, stop and resolve the identity with the maintainer. The workflow uses GitHub OIDC and PyPI's short-lived publishing authorization. [PyPI security model](https://docs.pypi.org/trusted-publishers/security-model/)

## Review a candidate

On pull requests, `Release distributions` exports the exact PR head twice, builds each wheel from its corresponding source distribution, normalizes tar ownership and timestamps, and compares SHA-256 hashes. The source commit time sets the wheel timestamp. The build job uploads the matching wheel, source archive and `SHA256SUMS` as one immutable Actions artifact named `distributions-<full-commit>`.

A separate runner retrieves this artifact by ID, verifies checksums, checks metadata with `twine check --strict`, and installs each distribution in a fresh environment. For each it runs the suite, compares installed skill files with the canonical tree, and builds the synthetic album offline with the regression dependency versions. The ordinary package CI also exercises the supported Python versions and the Windows installer.

To reproduce the release build locally, use Python 3.12 in an isolated development environment with `build==1.6.1`, `setuptools==84.2.1` and `wheel==0.48.0`, then run `python tools/build_release.py dist/review` in a Git checkout. Use an empty output directory. Compare platform builds using the same interpreter, build tools and compression libraries.

## Publish after approval

The owner must authorize the production dispatch and post-publication registry tests. The pending publisher and environment settings establish trust for that later run.

1. Merge the reviewed candidate. Confirm the full commit SHA on `main`, the package version, and green post-merge CI. Create and push an annotated tag, for example `v0.2.1`, on that exact commit.
2. Open **Actions → Release distributions → Run workflow**. Select branch `main`, enter the annotated tag and paste the full release commit SHA into the **commit** input. The workflow verifies the tag object, its target, the package version and both environment protection rules.
3. Review the new build and verification jobs for that final commit. Compare the two files and their checksums in the run artifact. Approve the waiting **pypi** deployment. The privileged job downloads the same artifact by ID and rechecks its manifest and package hashes. It passes just the two verified files to the PyPA publishing action with attestations enabled. [PyPI publishing action](https://github.com/pypa/gh-action-pypi-publish) · [PyPI attestations](https://docs.pypi.org/attestations/producing-attestations/)
4. Check the public project page, the released version, file digests and provenance on PyPI. Compare each digest with the verified manifest. In separate clean environments test `uv tool install wechat-sticker-publisher` and `pipx install wechat-sticker-publisher`, verify the CLI version, then build the public sample. Advertise the package-index commands after these tests succeed.

A GitHub Release is a separate publication decision. Its download assets can use the verified distributions from the final-commit workflow run. Preserve existing versions and their artifacts.
