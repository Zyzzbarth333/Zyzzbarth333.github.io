"""Summarise an MCAP bag from its index only: chunks, time span and channels. Reads the summary at the end of the file."""
import sys
from mcap.reader import make_reader
path = sys.argv[1]
with open(path, 'rb') as f:
    r = make_reader(f)
    s = r.get_summary()
    ch = s.chunk_indexes
    t0 = min(c.message_start_time for c in ch); t1 = max(c.message_end_time for c in ch)
    sizes = sorted(c.chunk_length for c in ch)
    print(f'chunks {len(ch)}, span {(t1 - t0) / 1e9:.1f} s, start {t0}, chunk size median {sizes[len(sizes)//2]/1e6:.1f} MB max {sizes[-1]/1e6:.1f} MB')
    print('chunk time span median', sorted((c.message_end_time - c.message_start_time) / 1e9 for c in ch)[len(ch)//2], 's')
    print('channels', len(s.channels))
