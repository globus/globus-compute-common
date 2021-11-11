### Added

- A new subpackage, `funcx_common.messagepack` provides an implementation of
  serialization and deserialization of message objects meant to be compatible
  with `funcx_endpoint.executors.high_throughput.messages` in its on-the-wire
  representation of messages. Changes between the two implementations are
  noted in a README for `messagepack`.
  - `messagepack` defines protocol versions, starting with the current and
    unversioned v0, for handling changes to the protocol over time
  - only v0 is implemented, but a suggested plan for v1 of the protocol can be
    seen in the `messagepack` readme
