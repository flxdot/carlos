import pytest

from .utils import crc8


@pytest.mark.parametrize(
    "data, crc_init, crc_final_xor, polynomial, expected_crc",
    [
        pytest.param(
            b"\xbe\xef", 0xFF, 0x00, 0x31, 0x92, id="Example from SHT30 datasheet"
        ),
    ],
)
def test_crc8(
    data: bytes, crc_init: int, crc_final_xor: int, polynomial: int, expected_crc: int
):
    """This function ensures that the CRC-8 algorithm yield the correct results."""

    crc = crc8(
        data=data,
        crc_init=crc_init,
        crc_final_xor=crc_final_xor,
        polynomial=polynomial,
    )
    assert (
        crc == expected_crc
    ), f"The CRC-8 is not correct. Expected: {expected_crc}, got: {crc}"
