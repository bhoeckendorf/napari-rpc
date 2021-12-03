from typing import Optional, Tuple, Union

import lzo
import numpy as np
import xarray as xr

from .protos import napari_pb2 as _napari_pb2


def decode_ndarray(
        ndarray: _napari_pb2.NdArray
) -> Tuple[np.ndarray, Tuple[float, ...], str]:
    """
    Decodes numpy array from network message.

    :param ndarray: from message
    :return: array (np.ndarray), spacing (Tuple[float, ...]), axes (str)
    """
    array = np.frombuffer(
        lzo.decompress(ndarray.array),
        dtype=np.dtype(ndarray.dtype)
    ).reshape(ndarray.shape)
    return array, tuple(ndarray.spacing), ndarray.axes


def _get_spacing_and_axes(x: xr.DataArray) -> Tuple[Tuple[float, ...], str]:
    axes = ""
    for i in map(str, x.dims):
        if len(i) != 1:
            raise ValueError(f"Axis '{i}' unsupported because len != 1.")
        axes += i
    spatial_axes = filter(lambda x: x in "zyx", axes)
    spacing = tuple(x.coords[i].values[1] - x.coords[i].values[0] if i in x.coords else 1.0 for i in spatial_axes)
    return spacing, axes


def encode_ndarray(
        array: Union[xr.DataArray, np.ndarray],
        spacing: Optional[Tuple[float, ...]] = None,
        axes: Optional[str] = None
) -> _napari_pb2.NdArray:
    """
    Encodes numpy array to be added to network message.

    :param array:
    :param spacing:
    :param axes:
    :return: array ready to be sent over network
    """
    if isinstance(array, xr.DataArray):
        spacing, axes = _get_spacing_and_axes(array)
        return encode_ndarray(array.data, spacing, axes)
    return _napari_pb2.NdArray(
        dtype=str(array.dtype),
        axes="".join(["?" for _ in range(array.ndim)]) if axes is None else axes,
        shape=array.shape,
        spacing=[1.0 for _ in range(array.ndim)] if spacing is None else spacing,
        array=lzo.compress(array.tobytes())
    )
