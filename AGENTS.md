# WeChat Sticker Publisher

Use the repository skill at `.agents/skills/wechat-sticker-publisher/SKILL.md` for creator workflows. Run the CLI against the creator’s project directory. Keep publishing behavior in the Python implementation so agents and offline CLI users receive the same results.

Keep the public example reproducible from its drawing script. Use synthetic inputs for tests. Retain the dated evidence for rule changes and run the test suite before releasing.

Maintain the portable skill only in `.agents/skills/wechat-sticker-publisher/`. Setuptools packages those files into the wheel. Adapters may select a discovery path but must invoke the same `wechat-sticker` commands. Test installers with isolated user and project roots. Record real discovery and agent-driven output separately from filesystem checks in [the compatibility matrix](docs/agent-compatibility.md).
