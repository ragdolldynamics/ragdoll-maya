Write about this.

```py
def view_to_pixmap(size=None):
    """Render currently active 3D viewport as a QPixmap"""

    # Python 2 backwards compatibility
    try:
        long
    except NameError:
        long = int

    image = om.MImage()
    view = omui.M3dView.active3dView()
    view.readColorBuffer(image, True)

    # Translate from Maya -> Qt jargon
    image.verticalFlip()

    osize = size or QtCore.QSize(512, 256)
    isize = image.getSize()
    buf = ctypes.c_ubyte * isize[0] * isize[1]
    buf = buf.from_address(long(image.pixels()))

    qimage = QtGui.QImage(
        buf, isize[0], isize[1], QtGui.QImage.Format_RGB32
    ).rgbSwapped()

    return QtGui.QPixmap.fromImage(qimage).scaled(
        osize.width(), osize.height(),
        QtCore.Qt.KeepAspectRatio,
        QtCore.Qt.SmoothTransformation
    )


def pixmap_to_base64(pixmap):
    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)

    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, "png")

    return bytes(array.toBase64())


def base64_to_pixmap(base64):
    data = QtCore.QByteArray.fromBase64(base64)
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(data)
    return pixmap
```
