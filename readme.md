This repository is discontinued. Please use the napari plugin
[napari-remote-interaction](https://github.com/bhoeckendorf/napari-remote-interaction),
which is not based on this repository.

# napari RPC

Use [napari](https://github.com/napari/napari) remotely.

This is currently a proof of concept with severely limited functionality. 

## Usage

### Server
This is currently a proof of concept. Setup and teardown are performed manually.

Inside napari's IPython terminal, we'll start an RPC server that we can subsequently connect to, e.g. from a Jupyter 
instance running on another machine. Please note that closing napari before manually stopping the server may freeze 
napari 
instead of closing it.

```Python
# Excecute inside napari's IPython terminal.
# Start server; port argument is optional, default port is 50051
from napari_rpc import napari_server_start
server_handle = napari_server_start(port=50051)  

# Stop server
server_handle.stop()
```

### Client
We can now send images to the napari instance started above from another machine like this:
```Python
import numpy as np
import napari_rpc

# Start client; use hostname and port of server started above.
client = napari_rpc.NapariClient(hostname="localhost", port=50051)

# Create random test image, then send it to the server.
# Here, the image is a plain numpy array, so we'll add extra info
# just as if we were using napari.add_image
image_czyx = np.random.randint(0, 255, (2, 32, 64, 64), np.uint8)
client.add_image(image_czyx, scale=[2.0, 1.0, 1.0], channel_axis=0)

# napari should now display this image!


# Alternatively, we can send a xarray.DataArray
import xarray as xr
image = xr.DataArray(
    image_czyx,
    dims=list("czyx"),
    coords={
        "z": np.arange(image_czyx.shape[-3]) * 2,
        "y": np.arange(image_czyx.shape[-2]),
        "x": np.arange(image_czyx.shape[-1])
    }
)

client.add_image(image)


# Close client after we're done using it.
# This doesn't stop the server. We can create a new client to reconnect.
client.close()
```

## Limitations
* Currently, only `add_image` is implemented. Some arguments don't work the same way as `napari.add_image`, or 
  at all.
* Large images are currently unsupported (> 2<sup>32</sup> bytes after LZO compression).

## Installation
```shell
# Inside the environment where napari is run from
pip install git+https://github.com/bhoeckendorf/napari-rpc.git[server]

# Inside the environment where the data to be displayed is generated 
pip install git+https://github.com/bhoeckendorf/napari-rpc.git[client]

# Use both pip installs if the environment for display and processing is the same.

# Alternatively, to quickly generate a complete conda environment
curl -L https://raw.githubusercontent.com/bhoeckendorf/napari-rpc/master/conda.yml > napari-rpc.yml
conda env create -f napari-rpc.yml
```
