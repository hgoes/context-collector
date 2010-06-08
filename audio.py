import gst
import gobject
import sys
import threading

gobject.threads_init()

class AudioRecorder(threading.Thread):
    def __init__(self,fn):
        threading.Thread.__init__(self)
        self.fn = fn
        self.source = gst.element_factory_make("alsasrc")

        caps = gst.Caps("audio/x-raw-int, rate=8000, channels=2")

        filter = gst.element_factory_make("capsfilter")
        filter.set_property("caps", caps)

        enc = gst.element_factory_make("wavenc")
        #enc.set_property("quality",8)

        queue = gst.element_factory_make("queue")

        sink = gst.element_factory_make("filesink")
        sink.set_property("location",fn)

        self.pipe = gst.Pipeline()
        self.pipe.add(self.source,filter,enc,queue,sink)
        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect("message",self.on_message)
        
        gst.element_link_many(self.source,filter,enc,queue,sink)

    def on_message(self,bus,msg):
        if msg.type == gst.MESSAGE_EOS:
            self.pipe.set_state(gst.STATE_NULL)
        
    def run(self):
        self.pipe.set_state(gst.STATE_PLAYING)
    def stop(self):
        self.source.send_event(gst.event_new_eos())        
