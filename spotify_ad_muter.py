import subprocess
import time

CHECK_INTERVAL = 0.25
MUTED_VOLUME = 0

class SpotifyAdMuter:
    def __init__(self):
        self.last_was_ad = False
        self.last_good_volume = 70

    def run_applescript(self, script):
        try:
            return subprocess.check_output(
                ["/usr/bin/osascript", "-e", script],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
        except:
            return None

    def spotify_running(self):
        script = '''
        tell application "System Events"
            return (exists process "Spotify")
        end tell
        '''
        result = self.run_applescript(script)
        return result == "true"

    def get_track_info(self):
        script = '''
        tell application "Spotify"
            set n to name of current track
            set a to artist of current track
            set d to duration of current track
            set v to sound volume
            set i to id of current track
            return n & "|||" & a & "|||" & d & "|||" & v & "|||" & i
        end tell
        '''
        result = self.run_applescript(script)
        if not result:
            return None
        try:
            n, a, d, v, i = result.split("|||")
            return n.strip(), a.strip(), int(d), int(v), i.strip()
        except:
            return None

    def set_volume(self, vol):
        self.run_applescript(
            f'tell application "Spotify" to set sound volume to {vol}'
        )

    def is_ad(self, name, artist, duration, track_id):
        n = name.lower()
        if "advertisement" in n:
            return True
        if track_id.startswith("spotify:ad:"):
            return True
        if duration == 0 and not name and not artist:
            return True
        return False

    def run(self):
        while True:
            if not self.spotify_running():
                time.sleep(1)
                continue

            info = self.get_track_info()
            if not info:
                time.sleep(CHECK_INTERVAL)
                continue

            name, artist, duration, volume, track_id = info

            if volume > 0 and not self.last_was_ad:
                self.last_good_volume = volume

            ad = self.is_ad(name, artist, duration, track_id)

            if ad and not self.last_was_ad:
                self.set_volume(MUTED_VOLUME)
                self.last_was_ad = True

            elif not ad and self.last_was_ad:
                self.set_volume(self.last_good_volume)
                self.last_was_ad = False

            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    SpotifyAdMuter().run()

