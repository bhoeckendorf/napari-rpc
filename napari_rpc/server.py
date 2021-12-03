from concurrent import futures

import grpc
import napari
from qtpy.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from .protos import napari_pb2 as _napari_pb2, napari_pb2_grpc as _napari_pb2_grpc
from .util import *


class NapariServicer(_napari_pb2_grpc.NapariServicer, QObject):
    image_added = Signal(object)
    exception_raised = Signal(str)

    def __init__(self, parent=None):
        _napari_pb2_grpc.NapariServicer.__init__(self)
        QObject.__init__(self, parent)
        self.server = None

    def AddImage(self, request, context):
        array, spacing, axes = decode_ndarray(request.data)
        kwargs = {"data": array, "scale": spacing}

        try:
            kwargs["channel_axis"] = axes.index("c")
        except ValueError:
            pass

        # if request.name is not None:
        #     kwargs["name"] = request.name

        self.image_added.emit(kwargs)
        return _napari_pb2.IsOkReply(has_error=False)


class NapariInteractor(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewer = napari.current_viewer()

    @Slot(object)
    def on_image_added(self, kwargs):
        self.viewer.add_image(**kwargs)

    @Slot(str)
    def on_exception_raised(self, msg):
        print(msg)


class NapariServicerRunnable(QRunnable):

    def __init__(self, servicer, port=50051):
        super().__init__()
        self._servicer = servicer
        self.port = port
        self._server = None

    def __del__(self):
        self.stop()

    def run(self):
        try:
            self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
            _napari_pb2_grpc.add_NapariServicer_to_server(self._servicer, self._server)
            self._server.add_insecure_port(f"[::]:{self.port}")
            self._server.start()
            self._server.wait_for_termination()
        except Exception as ex:
            print(ex)
            self._servicer.exception_raised.emit(str(ex))

    def stop(self, grace=None):
        if self._server is not None:
            self._server.stop(grace)


def napari_server_start(port=50051):
    qt_parent = napari.current_viewer().window.qt_viewer
    interactor = NapariInteractor(qt_parent)
    servicer = NapariServicer(qt_parent)
    servicer.image_added.connect(interactor.on_image_added)
    servicer.exception_raised.connect(interactor.on_exception_raised)
    runnable = NapariServicerRunnable(servicer, port)
    QThreadPool.globalInstance().start(runnable)
    return runnable
