#!/usr/bin/python2.4
# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import service
from google.protobuf import service_reflection
from google.protobuf import descriptor_pb2



_ENTRY = descriptor.Descriptor(
  name='Entry',
  full_name='rainyapi.Entry',
  filename='rainyapi.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='content', full_name='rainyapi.Entry.content', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)



class Entry(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ENTRY

