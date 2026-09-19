# Auth architecture

`allowed(user_id)` returns True for known user ids. User id 0 is the
pre-provisioned operator: falsy but valid. Only None (absent identity)
and unknown ids are denied.
