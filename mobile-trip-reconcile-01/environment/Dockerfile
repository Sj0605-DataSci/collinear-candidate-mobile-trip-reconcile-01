# --- amd64libs stage: extracts the x86_64 libc/loader Google's adb binary
# needs (Google publishes platform-tools for linux-amd64 only -- there is no
# official linux-aarch64 build). Requires the HOST's Docker daemon to have
# QEMU binfmt registered for cross-platform image pulls/builds (see
# README.md "Host prerequisites") -- same disclosed special-resource
# requirement this task needs at runtime anyway for adb itself to execute. ---
FROM --platform=linux/amd64 ubuntu:24.04 AS amd64libs
RUN mkdir -p /out/lib64 \
    && cp -r /usr/lib/x86_64-linux-gnu /out/x86_64-linux-gnu \
    && cp /usr/lib64/ld-linux-x86-64.so.2 /out/lib64/

# --- main stage: Ubuntu 24.04 (glibc 2.39), not Debian bookworm (glibc
# 2.36) -- the unofficial emulator build requires GLIBC_2.38+, found the
# hard way via a real boot failure ("version `GLIBC_2.38' not found"). ---
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 libx11-6 libxext6 libxrender1 curl ca-certificates unzip zstd \
    nodejs npm ripgrep \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g @openai/codex

# x86_64 runtime libs for adb (executed via the host's QEMU binfmt handler)
COPY --from=amd64libs /out/x86_64-linux-gnu /lib/x86_64-linux-gnu
COPY --from=amd64libs /out/lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2

ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
WORKDIR /opt/android-sdk

# generous timeouts + retries on every download -- plain curl -fsSL hit real
# transient exit-28 (operation timeout) failures on the larger archives here
ENV CURL=" curl --retry 5 --retry-delay 5 --connect-timeout 30 --max-time 1200 -fSL "

# unofficial ARM64 Android Emulator build, validated on this exact DGX Spark
# kernel (6.17.0-1032-nvidia) -- see README.md for the trust/provenance note.
# Vendored (not curl-fetched) because release-assets.githubusercontent.com
# (the CDN github.com's own release download redirects to) is unreachable
# from this network -- github.com itself resolves fine, but the asset CDN
# times out at TCP connect, a real environment-specific reachability gap,
# not a transient blip (confirmed via direct curl -v). Origin URL for
# provenance/re-verification:
# https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst
COPY emu.tar.zst /opt/android-sdk/emu.tar.zst
RUN echo "aaa426635e9b760567931e98f2de260f6323d46855f54067eb1401061f80c265  emu.tar.zst" | sha256sum -c - \
    && mkdir -p /tmp/emu-extract && tar --zstd -xf emu.tar.zst -C /tmp/emu-extract \
    && mv /tmp/emu-extract/emulator /opt/android-sdk/emulator \
    && rm -rf emu.tar.zst /tmp/emu-extract

# Google's x86_64-only platform-tools (adb), run via QEMU binfmt
RUN eval "$CURL" -o pt.zip https://dl.google.com/android/repository/platform-tools-latest-linux.zip \
    && unzip -q pt.zip && rm pt.zip

# Android 14 (API 34) arm64-v8a system image
RUN mkdir -p system-images/android-34/google_apis/arm64-v8a \
    && eval "$CURL" -o img.zip https://dl.google.com/android/repository/sys-img/google_apis/arm64-v8a-34_r14.zip \
    && unzip -q img.zip -d system-images/android-34/google_apis/arm64-v8a \
    && mv system-images/android-34/google_apis/arm64-v8a/arm64-v8a/* system-images/android-34/google_apis/arm64-v8a/ \
    && rmdir system-images/android-34/google_apis/arm64-v8a/arm64-v8a \
    && rm img.zip

# hand-authored AVD config (avdmanager isn't used -- see private build notes;
# this bypasses a spurious "emulator package must be installed" check from a
# too-new avdmanager that doesn't recognize a manually-placed emulator dir)
RUN mkdir -p /root/.android/avd/trip-avd.avd
COPY trip-avd.ini /root/.android/avd/trip-avd.ini
COPY config.ini /root/.android/avd/trip-avd.avd/config.ini

# agent-facing tool scripts + shared modules
COPY android_tools.py mobile_state.py screenshot.py tap.py swipe.py type_text.py \
     home.py back.py wait.py long_press.py recents.py notification_shade.py volume.py \
     seed_device_state.py notification_watcher.py \
     boot_emulator.sh content_seed.json /app/
RUN chmod +x /app/boot_emulator.sh

# TripDesk server + its (non-secret) catalog -- the true required constraints
# live only in tests/answer_key.json, never copied here
COPY private/tripdesk_server.py private/catalog.json /app/private/

RUN mkdir -p /app/output /data /var/log

ENTRYPOINT ["/app/boot_emulator.sh"]
CMD ["sleep", "infinity"]
