import rtmidi2 as rt
import mido


class MidiHandler:
    def __init__(self, callback):
        self.midi_in = rt.MidiIn()
        self.midi_out = rt.MidiOut()
        self.midi_in.callback = callback
        self.midi_in_name = ""
        self.midi_out_name = ""
        self.initialise()

    def initialise(self):
        self.set_midi_in("MPKmini")
        self.set_midi_out("Internal MIDI")

    @staticmethod
    def name_match(name, port_name):
        return name in port_name or port_name in name
    
    def get_in_ports(self):
        return rt.get_in_ports()
    
    def get_out_ports(self):
        return rt.get_out_ports()

    def check_safe_input(self, port_name):
        safe = False
        try:
            ports = mido.get_input_names()
            for port in ports:
                if self.name_match(port, port_name):
                    p = mido.open_input(port)
                    p.close()
                    safe = True
                    break
        except Exception as e:
            print(e)
        return safe

    def check_safe_output(self, port_name):
        safe = False
        try:
            ports = mido.get_output_names()
            for port in ports:
                if self.name_match(port, port_name):
                    p = mido.open_output(port)
                    p.close()
                    safe = True
                    break
        except Exception as e:
            print(e)
        return safe

    def set_midi_in(self, input_name):
        if self.midi_in_name is not None:
            self.midi_in.close_port()

        # safe = self.check_safe_input(input_name)
        try:
            rt_index = self.midi_in.ports_matching(f"*{input_name}*")[0]
            self.midi_in.open_port(rt_index)
            self.midi_in_name = self.midi_in.get_port_name(rt_index)
            return self.midi_in_name
        except Exception as e:
            print(f"Input port {input_name} could not be opened - it may be in use by another program.")
            return None

    def set_midi_out(self, output_name=None):
        if self.midi_out is not None:
            self.midi_out.close_port()

        # safe = self.check_safe_output(output_name)
        # print(output_name, "safe?", safe)
        try:
            rt_index = self.midi_out.ports_matching(f"*{output_name}*")[0]
            self.midi_out.open_port(rt_index)
            self.midi_out_name = self.midi_out.get_port_name(rt_index)
            return self.midi_out_name
        except Exception as e:
            print(f"Output port {output_name} could not be opened - it may be in use by another program.")
            return None

    def send_timing_clock(self):
        self.midi_out.send_raw(rt.TIMING_CLOCK)

    def send_midi_start(self):
        self.midi_out.send_raw(rt.SONG_START)

    def send_midi_stop(self):
        self.midi_out.send_raw(rt.SONG_STOP)

    def send_cc(self, channel, control, value):
        # self.midi_out.send_message([CONTROL_CHANGE | channel, control, value])
        try:
            self.midi_out.send_cc(channel, control, value)
        except OverflowError as e:
            print(f"OverflowError: CC: {channel}, {control}, {value}, {e}")

    def send_pitch_bend(self, channel, value=8192):
        # msg = [(PITCH_BEND & 0xF0) | (channel & 0xF), value & 0x7F, (value >> 7) & 0x7F]
        self.midi_out.send_pitchbend(channel, value)

    def note_on(self, channel, note, velocity):
        try:
            self.midi_out.send_pitchbend(channel, 8192)
            self.midi_out.send_noteon(channel, note, velocity)
        except OverflowError:
            print(f"OverflowError: NOTE ON: {channel}, {note}, {velocity}")

    def note_off(self, channel, note):
        # print(f"sending note off on channel {channel}; note {note}")
        try:
            self.midi_out.send_noteoff(channel, note)
        except OverflowError:
            print(f"OverflowError: NOTE OFF: {channel}, {note}")

    def all_notes_off(self, ch, all_sounds=False):
        m = rt.ALL_SOUND_OFF if all_sounds else rt.ALL_NOTES_OFF
        self.midi_out.send_cc(ch, m, 0)