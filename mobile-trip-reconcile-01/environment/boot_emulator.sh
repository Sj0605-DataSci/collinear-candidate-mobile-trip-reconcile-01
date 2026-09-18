#!/bin/bash
# ENTRYPOINT: boots the emulator, seeds device state, starts TripDesk and the
# notification watcher, then hands off to whatever CMD Harbor supplies (its
# base compose file sets this to `sleep infinity`, which is what keeps the
# container alive for docker-exec-based tool invocation).
set -u
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
ADB=/opt/android-sdk/platform-tools/adb

echo "[boot] starting emulator..."
"$ANDROID_HOME/emulator/emulator" -avd trip-avd -no-window -no-audio -no-snapshot \
    -no-boot-anim -gpu swiftshader_indirect > /var/log/emulator.log 2>&1 &

echo "[boot] waiting for boot_completed..."
deadline=$((SECONDS + 300))
while [ $SECONDS -lt $deadline ]; do
    status="$("$ADB" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
    if [ "$status" = "1" ]; then
        echo "[boot] boot completed after ${SECONDS}s"
        break
    fi
    sleep 2
done

echo "[boot] suppressing Chrome first-run noise (welcome screen, notifications nag, etc -- incidental app chrome, not designed task difficulty)..."
"$ADB" shell 'echo "chrome --no-first-run --disable-fre --disable-search-engine-choice-screen --no-default-browser-check" > /data/local/tmp/chrome-command-line'
# the "Chrome notifications make things easier" dialog is Android 13+'s
# runtime POST_NOTIFICATIONS permission prompt, not a Chrome FRE screen --
# --disable-fre doesn't touch it; pre-granting the permission does.
"$ADB" shell pm grant com.android.chrome android.permission.POST_NOTIFICATIONS

echo "[boot] starting TripDesk server..."
python3 /app/private/tripdesk_server.py > /var/log/tripdesk.log 2>&1 &

sleep 2
echo "[boot] seeding device state..."
python3 /app/seed_device_state.py 2>&1 | tee /var/log/seed.log

echo "[boot] starting notification watcher..."
python3 /app/notification_watcher.py > /var/log/notification_watcher.log 2>&1 &

echo "[boot] ready -- handing off to: $*"
exec "$@"
