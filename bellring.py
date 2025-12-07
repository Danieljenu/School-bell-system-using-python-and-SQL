"""
ringBell(schedule_list, audio_file='bell.mp3', check_interval=20, volume=0.8)

- schedule_list: list of timings. Examples:
    ['9', '09:00', '9:00', "9 o'clock", '9am', '7pm', '15:30']
- audio_file: path to a bell audio file (mp3/wav). Example: 'bell.mp3'
- check_interval: how often (seconds) to check the clock (default 20s)
- volume: 0.0 .. 1.0 (default 0.8)
"""

import re
import time
from datetime import datetime, date
import pygame

def _parse_time_string(tstr):
    """
    Parse many common time formats -> (hour, minute)
    Supported: '9', '09:00', '9:00', "9 o'clock", '9am', '9 am', '7pm', '07:30pm', '15:30'
    Returns (hour, minute) in 24-hour clock as ints, or raises ValueError.
    """
    s = str(tstr).strip().lower()
    # remove "o'clock"
    s = s.replace("o'clock", "").replace("o clock", "").strip()
    # detect am/pm
    ampm = None
    match_ampm = re.search(r'\b(am|pm)\b', s)
    if match_ampm:
        ampm = match_ampm.group(1)
        s = re.sub(r'\b(am|pm)\b', '', s).strip()

    # If it contains colon, split
    if ':' in s:
        parts = s.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {tstr}")
        h = int(parts[0])
        m = int(re.sub(r'\D', '', parts[1]) or 0)
    else:
        # try to extract number
        m = 0
        num_match = re.search(r'(\d{1,2})', s)
        if not num_match:
            raise ValueError(f"Invalid time format: {tstr}")
        h = int(num_match.group(1))

    # apply am/pm if present
    if ampm:
        if ampm == 'am':
            if h == 12:
                h = 0
        else:  # pm
            if h != 12:
                h = h + 12

    # normalize hour/minute ranges
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Parsed time out of range: {h}:{m:02d} from '{tstr}'")

    return (h, m)

def ringBell(schedule_list, audio_file='bell.mp3', check_interval=20, volume=0.8):
    """
    Main function. Blocks and checks the time every `check_interval` seconds.
    Plays audio_file when current time matches any time in schedule_list.
    """
    # parse and deduplicate schedule into (hour, minute) tuples
    schedule = set()
    for t in schedule_list:
        try:
            hm = _parse_time_string(t)
            schedule.add(hm)
        except ValueError as e:
            print(f"Warning: couldn't parse '{t}': {e}")

    if not schedule:
        print("No valid times parsed from schedule_list. Exiting.")
        return

    print("Parsed schedule (24h):", sorted(schedule))

    # initialize pygame mixer
    try:
        pygame.mixer.init()
    except Exception as e:
        print("Error initializing audio (pygame). Make sure audio device is available.")
        print("Exception:", e)
        return

    try:
        pygame.mixer.music.load(audio_file)
    except Exception as e:
        print(f"Error loading audio file '{audio_file}': {e}")
        return

    # set volume (0.0 to 1.0)
    try:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    except Exception:
        pass

    # track which scheduled times have already rung today
    rung_today = set()
    today_date = date.today()

    print("ringBell started. Press Ctrl+C to stop.")
    try:
        while True:
            now = datetime.now()
            # reset rung_today at midnight
            if date.today() != today_date:
                today_date = date.today()
                rung_today.clear()

            current_hm = (now.hour, now.minute)

            # check every scheduled time. If it matches current hour & minute and not rung yet today -> ring
            for hm in schedule:
                if hm == current_hm and hm not in rung_today:
                    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Ringing bell for scheduled time {hm[0]:02d}:{hm[1]:02d} ...")
                    try:
                        pygame.mixer.music.play()
                        # wait until playback finishes
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    except Exception as e:
                        print("Error while playing audio:", e)
                    rung_today.add(hm)

            # sleep a short while before next check
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("Stopping ringBell (KeyboardInterrupt).")
    finally:
        pygame.mixer.quit()


# Example usage:
if __name__ == "__main__":
    # Example schedule: 9:00 AM, 10:30 AM, 3:00 PM, 7 PM (24-hour: 9:00, 10:30, 15:00, 19:00)
    schedule = ['9', '00:29', '15:00', '7pm','00:30','00:31','00:32']
    ringBell(schedule, audio_file='bell.mp3', check_interval=15, volume=0.9)
