import pytest

def test():
    with pytest.warns(None) as record:
        from plugins import LMS7002, ADF4002, Si5351, Proxy
    return True

if __name__ == '__main__':
    assert test()
