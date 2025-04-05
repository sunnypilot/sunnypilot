# Definitions

|    Branch    | Definition | Description                                                                                                                                                                                                                                 | Stability/Readiness |
|:------------:|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| `release-c3` | Release branch | Stable release branches. After testing on `staging-c3`, updates are pushed here and published publicly.                                                                                                                            | **Ready to Use:** Highly stable, recommended for most users. |
| `staging-c3` | Staging branch | Pre-release testing branches. Community feedback is essential to identify issues before public release.                                                                                                                                     | **Varied Stability:** Generally stable, but intended for testing before public release. |
|   `dev-c3`   | Development branches | Experimental branches with the latest features and bug fixes brought in manually. Expect bugs and braking changes.                                                                                                                          | **Experimental:** Least stable, suitable for testers and developers. |
|   `master`   | Primary development branch | All Pull Requests are merged here for future releases. CI automatically strips, minifies, and pushes changes to `staging-c3`. Running the `master` branch is suitable for development purposes but not recommended for non-development use. | **For Development Use:** Suitable for developers, may be unstable for general use. |

!!! tip
    Your feedback is invaluable. Testers, even without software development experience, are encourage to run `dev-c3` or `staging-c3` and report issues.
