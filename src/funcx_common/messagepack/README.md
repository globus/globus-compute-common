# messagepack

This subpackage defines a message passing protocol for funcx endpoints and the
forwarder to exchange information, called "messagepack".

Today, only the v0 implementation of the protocol exists, but under wrappers
which, in theory, could be used to support future protocol versions.

## Protocol Support, send and receive

Message sending specifies a protocol version defaulting to the lowest supported
version of the protocol in use. This ensures a broad range of compatibility
with readers of the messages.

When receiving a message, the first step is always to attempt to determine the
protocol version.

## Version Detection (v0 vs other versions)

In v0 of the protocol, messages are packed bytes with no header, wrapper, or
other version information.

Under future versions, an explicit protocol version field will be added.

As a result, the detection logic, until the removal of v0, will be as follows:
- Attempt to detect a protocol_version
- If detection fails, protocol_version=0
- Otherwise, protocol_version=<detected>

## Proposed Protocol Version 1

This section defines a proposal for Version 1 of the messagepack protocol.

v1 of the protocol does the following:
- messages are encoded as JSON objects
- the "protocol_version" field of the objects is always `1` (as an int)
- there is a "message_type" field which contains a string of the message type

For example, under protocol v1, a heartbeat request message can be formulated as

    {"protocol_version": 1, "message_type": "HEARTBEAT_REQ"}

A Task message can be formulated as

    {
        "protocol_version": 1,
        "message_type": "TASK",
        "task_id": task_id,
        "container_id": container_id,
        "task_buffer": task_buffer
    }

## Differences between messagepack and `funcx-endpoint` "messages"

messagepack is based off of message definitions provided by `funcx-endpoint`
and is meant to be fully interchangeable.

The on-the-wire format for v0 of the protocol is an exact match for the
wire-format provided by the `funcx-endpoint` messages.

However, the python objects provided by this module have some key differences,
detailed here.

### Messages do not pack themselves

Under `funcx-endpoint`, messages are objects providing implementations of
`pack()` and `unpack()` as a method and classmethod.  and `funcx-endpoint`
"messages"

messagepack is based off of message definitions provided by `funcx-endpoint`
and is meant to be fully interchangeable.

The on-the-wire format for v0 of the protocol is an exact match for the
wire-format provided by the `funcx-endpoint` messages.

However, the python objects provided by this module have some key differences,
detailed here.

### Messages do not pack themselves

Under `funcx-endpoint`, messages are objects providing implementations of
`pack()` and `unpack()` as a method and classmethod. In order to have protocol
version dispatch handled by a central source, and to disentangle common and
message-specific details, this is no longer the case.

Instead, a `MessagePacker` object is used to pack and unpack messages. i.e.

`funcx-endpoint` messages:

    Task().pack()

`funcx-common` messagepack:

    MessagePacker().pack(Task())

On the unpacking side, the `MessagePacker` can `unpack(buf: bytes)`. This
solves the multiple-dispatch between types (an enum) and classes in a cleaner
way.

However, each message must provide its own v0 implementation, as these vary too
much to be implemented by the protocol object in a unified way.

### Message attribute and method changes

Several message attributes have changed. This is a list of all changes.

- `Message.type` is now `Message.message_type` to avoid using a soft-keyword
- `payload` and `header` are no longer provided properties of `Message` objects
- `Task` does not define a method `set_local_container`
- `Task.task_buffer` is always a string, even after loading (in `funcx-endpoint`
  it is defined as a `str` and then assigned a `bytes` value)
