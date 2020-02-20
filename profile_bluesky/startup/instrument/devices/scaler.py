
"""
scaler support (area detectors handled separately)
"""

__all__ = [
    'scaler',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.scaler import ScalerCH
from ..utils import safeOphydName


class MyScaler(ScalerCH):

    def select_channels(self, chan_names=[]):
        '''Select channels based on the EPICS name PV

        Parameters
        ----------
        chan_names : Iterable[str] or None

            The names (as reported by the channel.chname signal)
            of the channels to select.
            If *None*, select all channels named in the EPICS scaler.
        '''
        self.match_names()  # name channels by EPICS names
        name_map = {}
        for i, s in enumerate(self.channels.component_names):
            channel = getattr(self.channels, s)
            # just in case the name is not yet safe
            channel.s.name = safeOphydName(channel.s.name)
            nm = channel.s.name  # as defined in scaler.match_names()
            if i == 0 and len(nm) == 0:
                nm = "clock"        # ALWAYS get the clock channel
            if len(nm) > 0:
                name_map[nm] = s

        # previous argument was chan_names=None to select all
        # include logic here that allows backwards-compatibility
        if len(chan_names or []) == 0:    # default setting
            chan_names = name_map.keys()

        read_attrs = []
        for ch in chan_names:
            try:
                read_attrs.append(name_map[ch])
            except KeyError:
                raise RuntimeError("The channel {} is not configured "
                                    "on the scaler.  The named channels are "
                                    "{}".format(ch, tuple(name_map)))

        self.channels.kind = "normal"
        self.channels.read_attrs = list(read_attrs)
        self.channels.configuration_attrs = list(read_attrs)

        for i, s in enumerate(self.channels.component_names):
            channel = getattr(self.channels, s)
            if s in read_attrs:
                channel.s.kind = "hinted"
            else:
                channel.s.kind = "normal"

scaler = MyScaler('3idb:scaler1', name='scaler')
scaler.select_channels()

"""
Q: Should we alias the specific channels as global symbols?

See example: https://github.com/aps-8id-dys/ipython-8idiuser/blob/148-layout/profile_bluesky/startup/instrument/devices/scaler.py#L130-L141

In [9]: device_read2table(scaler)                                                                                       
=============== =========== ==========================
name            value       timestamp                 
=============== =========== ==========================
Time            100000000.0 2020-02-20 12:52:35.610616
NRIXS__delayed1 0.0         2020-02-20 12:52:35.610616
NRIXS__delayed2 0.0         2020-02-20 12:52:35.610616
NRIXS__delayed3 0.0         2020-02-20 12:52:35.610616
NFS__total      0.0         2020-02-20 12:52:35.610616
NFS__delayed    0.0         2020-02-20 12:52:35.610616
NRIXS_tot_sum   0.0         2020-02-20 12:52:35.610616
NRIXS_dlyd_sum  0.0         2020-02-20 12:52:35.610616
scaler_time     10.0        2020-02-20 12:52:35.610616
=============== =========== ==========================
"""