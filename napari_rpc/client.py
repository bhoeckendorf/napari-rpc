import grpc

from .protos import napari_pb2 as _napari_pb2, napari_pb2_grpc as _napari_pb2_grpc
from .util import *


class NapariClient:

    def __init__(self, hostname="localhost", port=50051):
        self._channel = grpc.insecure_channel(f"{hostname}:{port}")
        self._stub = _napari_pb2_grpc.NapariStub(self._channel)

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass

    def close(self):
        self._channel.close()

    def add_image(self, data, *args, **kwargs):
        request = _napari_pb2.AddImageRequest(data=encode_ndarray(data), *args, **kwargs)
        response = self._stub.AddImage(request)
        print("Errors encountered:", response.has_error)
