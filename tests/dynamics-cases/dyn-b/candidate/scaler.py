"""Autoscaler (candidate: confirm sustained demand before scaling).

Scale up only after 300 steps of overload; scale down fast.
Autoscaling handles spikes, and fast scale-down saves cost.
"""
SCALE_DELAY = 300
