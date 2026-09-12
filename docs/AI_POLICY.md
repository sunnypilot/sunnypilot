# AI policy

## Why this exists

We use AI tools ourselves, so this isn't an anti-AI stance. The problem is people submitting code, issues, or comments they don't actually understand. AI makes that very easy to do, and it creates real work for reviewers who have to figure out what you meant when you can't explain it yourself.

If you're not going to put effort into understanding and verifying your submission, we're not going to put effort into reviewing it.

## The rule

You are responsible for everything you submit: code, PR descriptions, issues, bug reports, comments.

1. Understand what you submit. If a reviewer asks why you did something, you answer from your own understanding, not by re-prompting. If you can't do that, don't submit it.

2. Test your change. AI gets things wrong all the time. Run it, break it, confirm it actually works.

3. Driving fixes need real evidence. Attach a dongle ID, upload logs, and include segments that show the fix working. A route hash by itself proves nothing.

4. No AI-generated media (images, diagrams, videos) in issues or PRs.

## Disclosure

If AI tools helped you write something, say so. Add an `Assisted-by:` line in your commit message:

```
Assisted-by: GitHub Copilot
Assisted-by: Claude
```

Disclosing won't count against your PR. It helps reviewers know where to look. Hiding it and getting caught will.

## How we review

Reviewers are looking at whether you understand your own change. Can you explain it? Can you respond to feedback without re-prompting? Does your PR description say why you made the change, not just list what changed?

Good code from someone who used AI and understands what they wrote is fine. How you got there doesn't matter as long as you can stand behind it.

## What happens

Submissions that don't meet this bar get closed. If it keeps happening, you get blocked.

## Maintainers

Maintainers use AI at their discretion. They've earned that through sustained contribution and they know the codebase.
