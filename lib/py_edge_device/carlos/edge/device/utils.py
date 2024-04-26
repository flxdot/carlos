__all__ = ["crc8"]


def crc8(
    data: bytes, crc_init: int = 0x00, crc_final_xor: int = 0xFF, polynomial: int = 0x31
) -> int:
    """Calculates the CRC-8 of the given data.

    :param data: The data to calculate the CRC-8 for.
    :param crc_init: The initial value of the CRC.
    :param crc_final_xor: The final XOR value of the CRC.
    :param polynomial: The polynomial of the CRC.
    :return: The CRC-8 of the data.
    """
    crc = crc_init

    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
        crc &= 0xFF

    return crc ^ crc_final_xor
