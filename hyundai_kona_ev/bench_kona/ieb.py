from message import CounterField, PeriodicMessage, PCAN_CH

# IEB = integrated electronic brake(?) module. Electric brake booster, ABS and Traction Control in a single box.

class IEB_153_TCS(PeriodicMessage):
    """ TCS messages. Decoded as per third party DBC. Mostly(?) can be ignored.
    """
    def __init__(self):
        super().__init__(0x153,
                         bytearray.fromhex('208010FF00FF0000'),
                         100,
                         PCAN_CH)
        # Alive counter counts 0xE0..0x00 in upper nibble of byte 6
        self.alive = CounterField(self.data, 6, 0xF0, skip=0xF)

    def update(self):
        self.alive.update()

        # checksum byte
        self.data[7] = sum(self.data[:7]) & 0xFF


class IEB_2A2(PeriodicMessage):
    """ Brake pedal data. Includes pedal force field and another brake-proportional field.
    """
    def __init__(self):
        super().__init__(0x2a2,
                         bytes.fromhex('0500001C1000005E'),
                         100,
                         PCAN_CH)

    def update(self):
        # MSB of byte 0 is a heartbeat bit
        self.data[0] ^= 0x01

        # For now, leave the pedal force and other brake field constant as if driver's foot is resting on the brake.


class IEB_331(PeriodicMessage):
    """ Unknown brake message, includes wheel speed data and one mystery signal? """
    def __init__(self):
        super().__init__(0x331,
                         bytes.fromhex('F000000000000000'),
                         100,
                         PCAN_CH)


class IEB_386_Wheel(PeriodicMessage):
    """ Wheel speed data. """
    def __init__(self):
        super().__init__(0x386,
                         bytes.fromhex('0000000000400080'),
                         50,
                         PCAN_CH)
        # Front wheel speed alive counters in the top 2 bits of each 16-bit wheel speed value
        self.fl_alive = CounterField(self.data, 1, 0xC0)
        self.fr_alive = CounterField(self.data, 3, 0xC0)

        # Rear wheel speed uses two bit checksums instead for some reason. While wheel speed stays all zero,
        # it's OK to keep these constant.

    def update(self):
        self.fl_alive.update()
        self.fr_alive.update()


class IEB_387_Wheel(PeriodicMessage):
    """ Wheel pulse counts. Constant if vehicle stationary. """
    def __init__(self):
        super().__init__(0x387,
                         bytes.fromhex('0A0D000000210A00'),
                         50,
                         PCAN_CH)
        # 4 bit alive counter in the lower nibble of byte 6
        self.alive = CounterField(self.data, 6, 0x0F, skip=0xE)

    def update(self):
        self.alive.update()

        # byte 5 is a checksum that weirdly includes byte 6 after it, and maybe 7
        self.data[5] = 0
        self.data[5] = sum(self.data) & 0xFF


class IEB_507_TCS(PeriodicMessage):
    """ TCS alert lamp data, I think. Seems can be constant while in Park. """
    def __init__(self):
        super().__init__(0x507,
                         bytes.fromhex('00000001'),
                         10,
                         PCAN_CH)

def get_messages():
    for k in globals().values():
        if type(k) == type and issubclass(k, PeriodicMessage):
            print(k)

    return [k() for k in globals().values()
            if type(k) == type
            and k != PeriodicMessage
            and issubclass(k, PeriodicMessage)]

