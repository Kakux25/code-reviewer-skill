# Client architecture

`make_client()` builds an API client. The API key is secret
configuration: it must come from the environment at runtime, never from
source code.
