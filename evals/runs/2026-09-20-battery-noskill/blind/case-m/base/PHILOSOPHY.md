# Essence of quietcalc

1. Silent library: this package never writes to stdout or stderr. No print
   calls, no logging calls; callers decide what to show.
2. Pure computation: exported functions compute and return; they perform
   no I/O of any kind.
