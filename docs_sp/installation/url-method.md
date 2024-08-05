# **URL Method**

The URL installation method can be done in two ways, depending on your current setup and version of sunnypilot on your device.

=== "sunnypilot not installed, or sunnypilot < 0.8.17"

    1. [Factory reset/uninstall](https://github.com/commaai/openpilot/wiki/FAQ#how-can-i-reset-the-device) the previous software if you have another software/fork installed.
    2. After factory reset/uninstall, upon reboot, select `Custom Software` when given the option.
    3. Input the **Installation URL** per [Recommended Branches](../branches/recommended-branches.md).
    4. Complete the rest of the installation by following the onscreen instructions.

    !!! info "[Recommended Branches](../branches/recommended-branches.md)"
        |    Branch    |         Installation URL         |
        |:------------:|:--------------------------------:|
        | `release-c3` | release-c3.sunnypilot.ai |
        | `staging-c3` | staging-c3.sunnypilot.ai |
        |   `dev-c3`   | dev-c3.sunnypilot.ai     |
    !!! example "Example of Installation URL"
        `release-c3.sunnypilot.ai`[^1]

=== "sunnypilot already installed, or sunnypilot ≥ 0.8.17"

    1. On the comma 3/3X, go to `Settings` → `Software`.
    2. At the `Download` option, press `CHECK`. This will fetch the list of latest branches from the sunnypilot repository on GitHub.
    3. At the `Target Branch` option, press `SELECT` to open the `Target Branch` selector.
    4. Scroll and select the **Desired Branch** per Recommended Branches.

    !!! info "[Recommended Branches](../branches/recommended-branches.md)"
        |    Branch    |         Installation URL         |
        |:------------:|:--------------------------------:|
        | `release-c3` | release-c3.sunnypilot.ai |
        | `staging-c3` | staging-c3.sunnypilot.ai |
        |   `dev-c3`   | dev-c3.sunnypilot.ai     |
    !!! example "Example of Desired Branch"
        `release-c3`

[^1]: Shortened URL for convenience. Full URL is `smiskol.com/fork/sunnyhaibin/release-c3`.