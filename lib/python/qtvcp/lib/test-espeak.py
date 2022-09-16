#!/usr/bin/env python3
from qtvcp import logger

LOG = logger.getLogger(__name__)

import os, sys

ESPEAK = False
try:
    from espeak import espeak
    import queue
    esQueue = queue.Queue()
    espeak.set_voice("m3")
    espeak.set_parameter(espeak.Parameter.Rate,160)
    espeak.set_parameter(espeak.Parameter.Pitch,1)
    ESPEAK = True
except:
    LOG.warning('audio alerts - Is python3-espeak installed? (sudo apt install python3-espeak)')


# new callback
def speak_synth_callback(*args):
    # when sentences ends, start the next one, until there are none.
    if args[0] == espeak.event_MSG_TERMINATED:
        if not esQueue.empty():
            espeak.synth(esQueue.get())


# the player class does the work of playing the audio hints
# http://pygstdocs.berlios.de/pygst-tutorial/introduction.html
class Player:
    def __init__(self):
        try:
            if "-old" in sys.argv:
                print("using old cb")
                espeak.set_SynthCallback(self.speak_finished)
            else:
                print("using new cb")
                espeak.set_SynthCallback(speak_synth_callback)
        except Exception as e:
            pass

    ###################
    # Espeak functions
    ###################
    def os_speak(self, f):
        cmd = f.lower().lstrip('speak')
        if ESPEAK:
            if '_kill_' in cmd:
                if espeak.is_playing():
                    self.speak_cancel()
                return
            try:
                # uses a queue so doesn't speak over it's self.
                esQueue.put(cmd)
                if not espeak.is_playing():
                    espeak.synth(esQueue.get())
            except Exception as e:
                print ('oops',e)
                # fallback call the system espeak - no queue used
                #os.system('''espeak -s 160 -v m3 -p 1 "%s" &''' % cmd)

    def speak_cancel(self):
        espeak.cancel()

    # old callback
    def speak_finished(self, *args):
        if args[0] == espeak.event_MSG_TERMINATED:
            if not esQueue.empty():
                espeak.synth(esQueue.get())



if __name__ == "__main__":
    try:
        test = Player()
        test.os_speak("hello")
        print('done')

    except Exception as e:
        print(e)
