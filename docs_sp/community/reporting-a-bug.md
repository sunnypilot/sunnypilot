# Bug Reports

sunnypilot is an actively maintained project that we constantly strive to improve. With project of this size and complexity, bugs may occur. If you think you have discovered a bug, you can help us by submitting an issue in our public [issue tracker](https://github.com/sunnypilot/sunnypilot/issues) or on our [Discord](https://discord.sunnypilot.ai), following this guide.

## Before creating an issue

With more than 2,500 users, issues are created frequently. The maintainers of this project are trying very hard to keep the number of open issues and reports down by fixing bugs as fast as possible. By following this guide, you will know exactly what information we need to help you quickly.

**But first, please do the following things before creating an issue.**

### Upgrade to the latest version

Chances are that the bug you discovered was already fixed in a subsequent version. Thus, before reporting an issue, ensure that you're running the [latest release version](https://github.com/sunnypilot/sunnypilot/releases) of sunnypilot. Please consult our [installation guide](../installation/index.md) to learn how to upgrade to the latest version.

!!! warning "Bug fixes are not backported"
    Please understand that only bugs that occur in the latest version of sunnypilot will be addressed. Also, to reduce duplicate efforts, fixes cannot be backported to earlier versions.

### Remove customizations

If you're using customized features, such as your own tweaks of the features or themes, please remove them from the branch you are testing from before reporting a bug. We can't offer official support for bugs that might hide in your implementations, so make sure to omit any customizations from the version being tested.

If, after removing the customizations, the bug is gone, the bug is likely caused by your customizations. A good idea is to add them back gradually to narrow down the root cause of the problem If you did a major version upgrade, make sure you adjusted all customizations you have implemented. If you are an advanced user, you could also utilize `git bisect` to perform a binary search in the history to find a particular regression.

!!! warning "Customizations mentioned in our documentation"
    A handful of the features sunnypilot offers can only be implemented with customizations. if you find a bug in any of the customizations that our documentations explicitly mentioned, you are, of course, encouraged to report it.

**Don't be shy to ask on our [Discord](https://discord.sunnypilot.ai) for help if you run into problems.**

### Search for solutions

At this stage, we know that the problem persists in the latest version and is not caused by any of your customizations. However, the problem might result from a small typo or a syntactical error in the source code, e.g., `selfdrive/car/interfaces.py`.

Now, before you go through the trouble of creating a bug report that is answered and closed right away with a link to the relevant documentation section or another already reported or closed issue or discussion, you can save time for us and yourself by doing some research:

1. [Search our documentation] and look for the relevant sections that could be related to your problem. If found, make sure that the settings are configured correctly.
2. [Search our Discord](https://discord.sunnypilot.ai) to learn if other users are struggling with similar problems and work together with our great comunity towards a solution. Many problems are solved there.
3. [Search our issue tracker](https://github.com/sunnypilot/sunnypilot/issues), as another user might already have reported the same problem, and there might even be a known workaround or fix for it. Thus, no need to create a new issue.

[Search our documentation]: ?q=

**Keep track of all <u>search terms</u> and <u>relevant links</u>, you'll need them in the bug report.**[^1]

  [^1]:
    We might be using terminology in our documentation different from yours, but we mean the same. When you include the search terms and related links in your bug report, you help us to adjust and improve the documentation. 

---

At this point, when you still haven't found a solution to your problem, we encourage you to report the issue on our [Discord](https://discord.sunnypilot.ai) because it's now very likely that you stumbled over something we don't know yet. Read the following section to learn how to create a complete and helpful bug report.


