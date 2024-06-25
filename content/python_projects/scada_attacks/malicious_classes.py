from scapy.contrib.modbus import *
from scapy.all import Raw
import random


# scuffed fix with the mini classes, will be fixed
class ModbusADUErrorResponse(ModbusADUResponse):
    name = "ModbusADU"
    fields_desc = ModbusADUResponse.fields_desc


class ModbusPDU03ReadHoldingRegistersError(Packet):
    name = "Read Holding Registers Response"
    fields_desc = [
        XByteField("funcCode", 0x00),
        XByteField("exceptCode", 0x00)
    ]


# RESPONSE INJECTIONS
class ResponseInjections:
    def naive_read_payload_size(self, packet):  # payload size is correct, but data is random zeros, ones or random bits
        packet = packet.copy()
        register_val = packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal; new_register_val = []

        chance = random.randint(0, 2)
        for a in register_val:
            numbers = [0, 1, random.randint(0, 1)]
            new_register_val.append(numbers[chance])

        packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal = new_register_val
        return packet

    def invalid_read_payload_size(self, packet):  # length does not conform to the requested length ( register value length is changed )
        packet = packet.copy()
        byte_count = packet[ModbusPDU03ReadHoldingRegistersResponse].byteCount
        register_val = packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal

        change_count = random.randint(-4, 4)
        if change_count == 0: change_count = 1
        if byte_count - change_count*2 <= 0: change_count = 1

        for a in range(0, abs(change_count)):
            if change_count < 0: register_val.pop()
            if change_count > 0: register_val.append(random.randint(0, 1))

        packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal = register_val
        return packet

    def invalid_exception_code(self, packet):  # returns false error response
        packet = packet.copy()
        try:
            function_code = str(packet[ModbusPDU03ReadHoldingRegistersResponse].funcCode)

            packet.funcCode = hex(int(f'0x8{function_code}', 16))
            packet.exceptCode = hex(int(f'0x0{random.randint(1, 8)}', 16))

            error_response = ModbusADUErrorResponse()

            error_response.transID = packet.transId
            error_response.protoId = packet.protoId
            error_response.len = packet.len + 1  # the exceptCode field
            error_response.unitId = packet.unitId

            error_response /= ModbusPDU03ReadHoldingRegistersError()  # SCUFFED fix

            error_response[ModbusPDU03ReadHoldingRegistersError].funcCode = int(function_code) + 128
            error_response[ModbusPDU03ReadHoldingRegistersError].exceptCode = random.randint(1, 8)

            packet = error_response

        except Exception as e: print(e)
        return packet

    def negative_sensor_measurements(self, packet):  # returns negative process measurements ( bad, because usually they are only positive )
        packet = packet.copy()
        register_val = packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal; new_register_val = []

        for a in register_val:
            new_register_val.append(a * -1)

        packet[ModbusPDU03ReadHoldingRegistersResponse].registerVal = new_register_val

        # idk this seems unneeded honestly

        return packet
