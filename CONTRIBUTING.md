# Contributing

Install Python 3.10+ and use a local virtual environment in a checkout. To install the development dependencies and run the tests:

```sh
python -m pip install -e '.[test]'
python -m pytest
python -m build
```

Tests use generated artwork and temporary project directories. Use synthetic inputs when reproducing a bug. Include the command, version, expected result and relevant validation findings. Remove private paths and images from reports.

Keep publishing decisions in the shared Python package. Add a focused regression test when changing image processing, validation, provider selection or archive behavior. Update the dated reference and the applicable tests together if a WeChat requirement changes. Document any runtime-dependent encoding differences.

The project accepts source code, documentation and original synthetic examples under MIT. Identify third-party components and their licenses in contributions. Each creator controls the rights to their own source artwork and packages, subject to underlying third-party rights.
