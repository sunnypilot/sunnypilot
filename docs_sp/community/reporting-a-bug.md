# Bug Reports

sunnypilot is an actively maintained project that we constantly strive to improve. With project of this size and complexity, 
bugs may occur. If you think you have discovered a bug, you can help us by submitting an issue 
in [comma's public issue tracker][comma's issue tracker], 
[sunnypilot's public issue tracker][sunnypilot's issue tracker] or on our [Discord][discord], following this guide.

  [comma's issue tracker]: https://github.com/commaai/openpilot/issues
  [sunnypilot's issue tracker]: https://github.com/sunnypilot/sunnypilot/issues
  [discord]: https://discord.sunnypilot.ai

## Before creating an issue

With more than 2,500 users, issues are created frequently. The maintainers of this project are trying very hard to keep 
the number of open issues and reports down by fixing bugs as fast as possible. By following this guide, you will know 
exactly what information we need to help you quickly.

**But first, please do the following things before creating an issue.**

### Upgrade to the latest version

Chances are that the bug you discovered was already fixed in a subsequent version. Thus, before reporting an issue, 
ensure that you're running the [latest release version](https://github.com/sunnypilot/sunnypilot/releases) of sunnypilot. 
Please consult our [installation guide](../setup/read-before-installing.md) to learn how to upgrade to the latest version.

!!! warning "Bug fixes are not backported"
    Please understand that only bugs that occur in the latest version of sunnypilot will be addressed. Also, to reduce 
    duplicate efforts, fixes cannot be backported to earlier versions.

### Remove customizations

If you're using customized features, such as your own tweaks of the features, please remove them from the branch 
you are testing from before reporting a bug. We can't offer official support for bugs that might hide in your implementations, 
so make sure to omit any customizations from the version being tested.

If, after removing the customizations, the bug is gone, the bug is likely caused by your customizations. A good idea is 
to add them back gradually to narrow down the root cause of the problem If you did a major version upgrade, make sure 
you adjusted all customizations you have implemented.

!!! tip
    If you are an advanced user, you could also utilize `git bisect` 
    to perform a binary search in the history to find a particular regression.

!!! warning "Customizations mentioned in our documentation"
    A handful of the features sunnypilot offers can only be implemented with customizations. if you find a bug in any of 
    the customizations that our documentations explicitly mentioned, you are, of course, encouraged to report it.

**Don't be shy to ask on our [Discord][discord] for help if you run into problems.**

### Search for solutions

At this stage, we know that the problem persists in the latest version and is not caused by any of your customizations. 
However, the problem might result from a small typo or a syntactical error in the source code, e.g., `selfdrive/car/interfaces.py`.

Now, before you go through the trouble of creating a bug report that is answered and closed right away with a link to
the relevant documentation section or another already reported or closed issue or discussion, you can save time for us 
and yourself by doing some research:

1. [Search our documentation] and look for the relevant sections that could be related to your problem. If found, make
    sure that the settings are configured correctly.
2. [Search our Discord][discord] to learn if other users are struggling with similar problems and work together with 
   our 
   great comunity towards a solution. Many problems are solved there.
3. [Search comma's openpilot issue tracker][comma's issue tracker], as another user might 
   already have reported the same problem that may exist in
   stock openpilot, and there might even be a known workaround or fix for it. Thus, no need to create a new issue.
4. [Search sunnypilot's issue tracker][sunnypilot's issue tracker], as another user might already have 
   reported the same problem, and there
   might even be a known workaround or fix for it. Thus, no need to create a new issue.

[Search our documentation]: ?q=

**Keep track of all <u>search terms</u> and <u>relevant links</u>, you'll need them in the bug report.**[^1]

  [^1]:
    We might be using terminology in our documentation different from yours, but we mean the same. When you include the 
    search terms and related links in your bug report, you help us to adjust and improve the documentation. 

---

At this point, when you still haven't found a solution to your problem, we encourage you to report the issue on our 
[Discord][discord] because it's now very likely that you stumbled over something we don't know 
yet. Read the following section 
to learn how to create a complete and helpful bug report.

## Issue template

We have created an issue template to make the bug reporting process as simple as possible, and more efficient for our
community and us.

- [Title]
- [Context]<small>optional</small>
- [Bug description]
- [Related links]
- [Reproduction]
- [Steps to reproduce]
- [Checklist]

  [Title]: #title
  [Context]: #context
  [Bug description]: #bug-description
  [Related links]: #related-links
  [Reproduction]: #reproduction
  [Steps to reproduce]: #steps-to-reproduce
  [Checklist]: #checklist

### Title

A good title is short and descriptive. It should be a one-sentence executive summary of the issue, so the impact and
severity of the bug you want to report can be inferred from the title.

| <!-- --> | Example                                                                                                      |
| -------- |--------------------------------------------------------------------------------------------------------------|
| :material-check:{ style="color: #4DB6AC" } __Clear__ | Speed Limit Control (SLC) stuck in `preActive` when engaged                                                  |
| :material-close:{ style="color: #EF5350" } __Wordy__ | The Speed Limit Control (SLC) remains in the `preActive` state when longitudinal it's supposed to be engaged |
| :material-close:{ style="color: #EF5350" } __Unclear__ | SLC does not work                                                                                            |
| :material-close:{ style="color: #EF5350" } __Useless__ | Help                                                                                                         |

### Context <small>optional</small> { #context }

Before describing the bug, you can provide additional context for us to understand what you were trying to achieve.
Explain the circumstances in which you're using sunnypilot, and what you _think_ might be relevant. Don't write 
about the bug here.

!!! note "__Why this might be helpful__"
    Some errors only manifest in specific settings, environments or edge cases, for example, when the feature is not available
    to certain cars.

### Bug description

Now, to the bug you want to report. Provide a clear, focused, specific, and concise summary of the bug you encountered. 
Explain why you think this is a bug that should be reported to sunnypilot, and not to one of its dependencies.[^3]
Adhere to the following principles:

  [^3]:
    Sometimes, users report bugs on our [sunnypilot's issue tracker] or [Discord][discord] 
    that are caused by one of our upstream dependencies, including [comma's openpilot], [comma's panda],
    or other openpilot forks' dependencies. A good rule of thumb is
    to reproduce the issue with stock openpilot in the same conditions and
    check if the problem persists. If it does, the problem is likely not
    related to sunnypilot and should be reported upstream. When in
    doubt, use our [Discord][discord] to ask for help.

  [comma's openpilot]: https://github.com/commaai/openpilot
  [comma's panda]: https://github.com/commaai/panda

-   __Explain the <u>what</u>, not the <u>how</u>__ – don't explain
    [how to reproduce the bug][Steps to reproduce] here, we're getting there.
    Focus on articulating the problem and its impact as clearly as possible.

-   __Keep it short and concise__ – if the bug can be precisely explained in one
    or two sentences, perfect. Don't inflate it – maintainers and future users
    will be grateful for having to read less.

-   __One bug at a time__ – if you encounter several unrelated bugs, please
    create separate issues for them. Don't report them in the same issue, as
    this makes attribution difficult.

---

:material-run-fast: __Stretch goal__ – if you found a workaround or a way to fix
the bug, you can help other users temporarily mitigate the problem before
we maintainers can fix the bug in our code base.

!!! note "__Why we need this__"
    In order for us to understand the problem, we need a clear description of it and quantify its impact, which is 
    essential for triage and prioritization.

### Related links

Of course, prior to reporting a bug, you have read our documentation and
[could not find a working solution][search for solutions]. Please share links
to all sections of our documentation that might be relevant to the bug, as it
helps us gradually improve it.

Additionally, since you have searched [comma's issue tracker], [sunnypilot's issue tracker] or [Discord][discord]
before reporting an issue, and have possibly found several issues or
discussions, include those as well. Every link to an issue or discussion creates
a backlink, guiding us maintainers and other users in the future.

---

:material-run-fast: __Stretch goal__ – if you also include the search terms you
used when [searching for a solution][search for solutions] to your problem, you
make it easier for us maintainers to improve the documentation.

  [search for solutions]: #search-for-solutions

### Reproduction

A minimal reproduction is at the heart of every well-written bug report, as
it allows us maintainers to instantly recreate the necessary conditions to
inspect the bug to quickly find its root cause. It's a proven fact that issues
with concise and small reproductions can be fixed much faster.

After you have created the reproduction, take note of your <u>__comma Dongle ID__</u>. It will be used during the bug 
report.

!!! note "__Why we need this__"
    If an issue contains no minimal reproduction or just a link to a repository with thousands of files, the 
    maintainers would need to invest a lot of time into trying to recreate the right conditions to even inspect the 
    bug, let alone fix it.

!!! warning "Don't share links to repositories"
    While we know that it is a good practice among developers to include a link
    to a repository with the bug report, we currently don't support those in our
    process. The reason is that the reproduction, which is automatically
    produced by the <u>__route ID__</u> contains all the necessary
    environment information that is often forgotten to be included.

    Additionally, there are many non-technical users of sunnypilot that
    have trouble creating repositories.

### Steps to reproduce

At this point, you provided us with enough information to understand the bug
and provided us with a reproduction that we could run and inspect. However, when
we check your reproduction, it might not be immediately apparent how we can see
the bug in action.

Thus, please list the specific steps we should follow when running your
reproduction to observe the bug. Keep the steps short and concise, and make sure
not to leave anything out. Use simple language as you would explain it to a
five-year-old, and focus on continuity.

!!! note "__Why we need this__"
    We must know how to navigate your reproduction in order
    to observe the bug, as some bugs only occur at certain viewports or in
    specific conditions.

### Uploading logs and preserving routes

After reproducing the bug, please follow these steps to upload the necessary logs and preserve the routes.

1. Ensure the route is fully uploaded at [comma Connect]. We cannot look 
  into issues without routes, or at least a comma Dongle ID.

    1. Visit [comma Connect], select the route with the issue reproduced.
    2. Under the "Files" button, locate "All logs". Click "Upload x files".
    3. View the upload queue, and confirm that all raw logs are uploaded.

    !!! note
        Sometimes when the qlogs of the route are still being uploaded, some raw logs may not be available to 
        request for upload. Refresh the page a few times once you have confirmed all qlogs have been uploaded, 
        then try to upload all raw logs again if available.

2. Share your Dongle ID with sunnypilot on [comma Connect].

    1. Visit [comma Connect], navigate to the gear icon.
    2. Select "Share by email", and enter `support@sunnypilot.ai`.
    3. Confirm the sharing by clicking the share icon again.
    4. Set the device name to your vehicle's year/make/model and your Discord username, so it can be easily identified.

3. Once all raw logs are uploaded, click "More info" and enable the "Preserved" option to preserve the route.
4. Attach the route ID in your issue submission.

  [comma Connect]: https://connect.comma.ai

### Checklist

Thanks for following the guide and creating a high-quality and complete bug
report – you are almost done. The checklist ensures that you have read this guide
and have worked to your best knowledge to provide us with everything we need to
know to help you.

- [ ] I have upgraded to the latest release version of sunnypilot.
- [ ] I have removed or disable any customizations and confirmed the bug persists.
- [ ] I have searched the documentation, issue trackers, and Discord for similar issues.
- [ ] I have created a minimal reproduction and noted my comma Dongle ID.
- [ ] I have shared my Dongle ID with sunnypilot at `support@sunnypilot.ai`.
- [ ] I have filled out all required sections of the issue template.

__We'll take it from here.__
