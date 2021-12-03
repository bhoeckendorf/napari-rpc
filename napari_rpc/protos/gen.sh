#!/usr/bin/env sh
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./napari.proto
patch napari_pb2_grpc.py enable_local_import.patch
