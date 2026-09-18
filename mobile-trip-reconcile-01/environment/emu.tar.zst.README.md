# emu.tar.zst not included in this repo

The vendored ARM64 Android emulator binary (~90MB) is excluded here to keep
the repo lean. To build this task, fetch it and place it at
`environment/emu.tar.zst` before running `harbor run`:

```
curl -fL -o environment/emu.tar.zst \
  https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst
echo "aaa426635e9b760567931e98f2de260f6323d46855f54067eb1401061f80c265  environment/emu.tar.zst" | sha256sum -c -
```

See `DESIGN_DOC.md` Section 7 for why this is vendored rather than
fetched at build time (the release-asset CDN was unreachable from the
build environment used for this submission), and `environment/Dockerfile`
for how it's consumed.
