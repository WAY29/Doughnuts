import base64


def try_decode_base64(sb):
    try:
        if isinstance(sb, str):
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            return sb
        if base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes:
            return base64.b64decode(sb_bytes).decode()
        return sb
    except Exception:
        return sb
