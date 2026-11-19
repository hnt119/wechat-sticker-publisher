# Optional artwork providers

Use a provider when you want new supplementary illustrations and are comfortable sending their creative context to the selected service. The default installation, validation, briefs and package builds run locally. Inspect the missing roles first.

```sh
wechat-sticker assets briefs --pack album
```

## OpenAI Images

From the toolkit checkout, install the optional SDK into the same Python environment as the CLI.

```sh
python -m pip install '.[openai]'
```

Set `OPENAI_API_KEY` in your shell or secret manager. Set `WECHAT_STICKER_IMAGE_MODEL` to an image model available to your API account that supports PNG generation and editing with the background types you need. The adapter requires an explicit model choice. OpenAI bills API usage to that account. [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)

```sh
wechat-sticker build --pack album --generate-missing --provider openai-images
```

The adapter requests one PNG per missing supplementary role. The prompt contains the album name, description, character identifiers, intended dimensions and drawing directions. With an empty manifest `references` list, it uses the Images generation endpoint. With references, it sends the listed single-frame PNG/JPEG illustrations to the Images edit endpoint in the specified order. It sends pixel-only PNGs with generic names. Select up to 16 approved references, each below 50 MB after PNG encoding. The SDK targets the official OpenAI endpoint and automatic SDK retries are disabled. [Image generation API](https://developers.openai.com/api/reference/python/resources/images/methods/generate) · [Image editing API](https://developers.openai.com/api/reference/python/resources/images/methods/edit)

Each build creates a fresh snapshot. Open the previews and check that generated art matches the character, composition and text. To reuse an approved result, copy the image from the release’s `supplementary/` folder into the creator project, then set its path in the manifest. Use `build --offline` for the next snapshot. Repeating `--generate-missing` while the source is absent can incur another charge. A timeout can occur after the service has accepted a billable request.

If setup or generation fails, the build records the missing role, saves the offline exports and includes a manual artwork brief. Check the two environment variables, the optional SDK installation, model access, reference format and your API account before retrying.

## Other providers

An installed Python package can register a class implementing `ArtworkProvider.generate(brief, references, destination)` in the `wechat_sticker_publisher.artwork` entry point group. The constructor takes no arguments. The method receives the structured artwork brief and approved local reference paths, and writes its PNG to the supplied temporary path. The core validates, sizes and packages the result. The provider owns authentication, network activity and error handling. Expose user-facing configuration errors through `ProviderSetupError` using messages that are safe to include in reports.
