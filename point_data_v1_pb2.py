# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: point_data_v1.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13point_data_v1.proto\x12\x0cpointdata.v1\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1bgoogle/protobuf/empty.proto\"\xc2\x01\n\rPeriodRequest\x12,\n\x08\x66romDate\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12*\n\x06toDate\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\r\n\x05group\x18\x03 \x01(\t\x12\r\n\x05\x63lass\x18\x04 \x01(\t\x12\r\n\x05kinds\x18\x05 \x03(\t\x12*\n\x05users\x18\x06 \x03(\x0b\x32\x1b.pointdata.v1.PointDataUser\"9\n\x10\x41\x64\x64PointsRequest\x12%\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x17.pointdata.v1.PointData\"\xf8\x01\n\tPointData\x12)\n\x04user\x18\x01 \x01(\x0b\x32\x1b.pointdata.v1.PointDataUser\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\r\n\x05group\x18\x03 \x01(\t\x12\r\n\x05\x63lass\x18\x04 \x01(\t\x12\x0c\n\x04kind\x18\x05 \x01(\t\x12\x0e\n\x06source\x18\x06 \x01(\t\x12\x0e\n\x06\x64\x65vice\x18\x07 \x01(\t\x12\x0f\n\x07\x63omment\x18\x08 \x01(\t\x12\r\n\x05value\x18\t \x01(\x01\x12*\n\x05\x63ount\x18\n \x01(\x0b\x32\x1b.google.protobuf.Int32Value\"1\n\rPointDataUser\x12\x0e\n\x06userId\x18\x01 \x01(\x05\x12\x10\n\x08tenantId\x18\x02 \x01(\x05\"7\n\x0eGetPointsReply\x12%\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x17.pointdata.v1.PointData2\x9f\x01\n\x10PointDataService\x12\x46\n\tGetPoints\x12\x1b.pointdata.v1.PeriodRequest\x1a\x1c.pointdata.v1.GetPointsReply\x12\x43\n\tAddPoints\x12\x1e.pointdata.v1.AddPointsRequest\x1a\x16.google.protobuf.EmptyB\x13\xaa\x02\x10Np.Engine.Api.V1b\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'point_data_v1_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\252\002\020Np.Engine.Api.V1'
  _PERIODREQUEST._serialized_start=132
  _PERIODREQUEST._serialized_end=326
  _ADDPOINTSREQUEST._serialized_start=328
  _ADDPOINTSREQUEST._serialized_end=385
  _POINTDATA._serialized_start=388
  _POINTDATA._serialized_end=636
  _POINTDATAUSER._serialized_start=638
  _POINTDATAUSER._serialized_end=687
  _GETPOINTSREPLY._serialized_start=689
  _GETPOINTSREPLY._serialized_end=744
  _POINTDATASERVICE._serialized_start=747
  _POINTDATASERVICE._serialized_end=906
# @@protoc_insertion_point(module_scope)