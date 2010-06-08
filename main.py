import audio
import movement

import sys
import subprocess

import gtk
import gobject
import datetime
import dateutil.tz as tz
import time
import annpkg.sources
import annpkg.model
import os

class Main(gtk.Window):
    def __init__(self):
        gobject.threads_init()
        profiles = ["Walking","Profile 2"]
        gtk.Window.__init__(self)
        self.set_title("Recorder")

        self.handle = open("profile.log",'a')

        self.task_audio = None
        self.task_movement = None
        
        box = gtk.VBox()

        chooser = gtk.combo_box_new_text()
        for profile in profiles:
            chooser.append_text(profile)

        self.button_rec = gtk.Button("Start")
        self.button_rec.connect("clicked",lambda but: self.toggle_recording())

        chooser.connect("changed",self.update_profile)

        box.pack_start(chooser,expand=False,fill=True)
        box.pack_start(self.button_rec,expand=False,fill=True)

        self.add(box)
        self.connect("destroy",lambda x: gtk.main_quit())

        self.show_all()
            
    def update_profile(self,chooser):
        now = time.time()
        print >>self.handle,now,chooser.get_active_text()

    def quit(self):
        if self.task_audio is not None:
            self.task_audio.stop()
            self.task_movement.stop()
            self.task_audio.join()
            self.task_movement.join()
        gtk.main_quit()

    def toggle_recording(self):
        if self.task_audio is None:
            self.button_rec.set_label("Stop")
            self.tm = datetime.datetime.utcnow()
            self.file_audio = self.tm.strftime("audio-%Y-%m-%d-%H:%M:%S.wav")
            self.file_acc = self.tm.strftime("acc-%Y-%m-%d-%H:%M:%S")
            self.task_audio = audio.AudioRecorder(self.file_audio)
            self.task_movement = movement.MovementReader(self.file_acc)
            self.task_audio.run()
            self.task_movement.start()
        else:
            self.button_rec.set_label("Start")
            self.task_audio.stop()
            self.task_movement.stop()
            self.task_movement.join()
            self.task_audio = None
            self.task_movement = None
            src_acc = annpkg.sources.MovementSource.from_file(self.file_acc,"m",(0,1))
            src_aud = annpkg.sources.AudioSource.from_file(self.file_audio,"aud",(0,1),self.tm)
            pkg = annpkg.model.AnnPkg([ (src,None) for src in src_acc+src_aud ],[])
            pkg.write(self.tm.strftime("recording-%Y-%m-%d-%H:%M:%S.tar"))
            os.remove(self.file_acc)
            os.remove(self.file_audio)
    def run(self):
        subprocess.call(["/usr/sbin/alsactl","restore","-f","/usr/share/openmoko/scenarios/voip-handset.state"])
        gtk.main()


Main().run()
