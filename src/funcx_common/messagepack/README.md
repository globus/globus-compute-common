# messagepack

This subpackage defines a message passing protocol for funcx endpoints and the
forwarder to exchange information, called "messagepack".

Today, only the v1 implementation of the protocol exists, but under wrappers
which could be used to support future protocol versions.

## Protocol Support, send and receive

Message sending specifies a protocol version defaulting to the lowest supported
version of the protocol in use. This ensures a broad range of compatibility
with readers of the messages.

When receiving a message, the first step is always to attempt to determine the
protocol version.

## Version Detection

The first byte of a message is the version byte. It contains a single
unsigned integer, and can be read without unpacking the message to get the
version of the protocol to use.

## Versions

### Protocol Version 0

A v0 of the protocol was implemented in the past, but it was removed.

### Protocol Version 1

In v1 of the protocol, messages are JSON payloads with a one byte header.
The leading byte is the version byte, and should always have a value of `1`.
This ensures that readers can check the protocol version without attempting to
unpack the message.

The rest of the payload contains a UTF-8 encoded JSON document with no
newlines.

Multiple messages can therefore be streamed using unix-style newlines (`\n`)
as the delimiter.

#### Missing and Unknown Field Behavior

In v1, message unpacking has the following behavior for unknown or missing
fields:

- If a payload does not contain a required field, an `InvalidMessagePayloadError`
  will be raised

- If a payload defines fields which are not recognized, they will be ignored

## Differences between messagepack and `funcx-endpoint` "messages"

messagepack is based off of message definitions provided by `funcx-endpoint`
and is meant as a replacement.

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

On the unpacking side, the `MessagePacker` can `unpack(buf: bytes)`.

### Message attribute and method changes

Several message attributes have changed. This is a list of all changes.

- `Message.type` is now `Message.message_type` to avoid using a soft-keyword
- `payload` and `header` are no longer provided properties of `Message` objects
- `Task` does not define a method `set_local_container`
- `Task.task_buffer` is always a string, even after loading (in `funcx-endpoint`
  it is defined as a `str` and then assigned a `bytes` value)
