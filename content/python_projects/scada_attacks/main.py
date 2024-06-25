import scapy.utils
from scapy.all import *
from scapy.contrib.modbus import *
import json

import random

import content.python_projects.scada_attacks.malicious_classes as malicious_classes
import content.python_projects.scada_attacks.iec104 as iec104


def main_function(current_protocol, attack_number):
    path = os.path.dirname(os.path.realpath(__file__))

    # json file in the future would be siiick
    json_information = {
        "modbus packets": rdpcap(path+'\\only_modbus.pcap'),
        "modbus response injections": malicious_classes.ResponseInjections(),

        "iec104 packets": rdpcap(path+'\\only_iec104.pcap'),
        "iec104 hack number": attack_number  # 5.2 or 5.4 currently, will probably import the rest later
    }

    packets = json_information[current_protocol + ' packets']

    # temporary fix
    try: response_injections = json_information[current_protocol + ' response injections']
    except KeyError: response_injections = None
    try: hack_number = json_information[current_protocol + ' hack number']
    except KeyError: hack_number = None

    new_packets = []

    phases = 0
    delay = 0

    if hack_number == '5.4' and current_protocol == 'iec104':
        iec104_packet_injection = iec104.Iec104PacketInjection()
    else: iec104_packet_injection = None

    # this below will be a CLASS in ze futura
    for packet in packets:
        if current_protocol == 'modbus':
            # response packets
            try:
                packet_choices = [response_injections.naive_read_payload_size(packet[ModbusADUResponse]),
                                  response_injections.invalid_read_payload_size(packet[ModbusADUResponse]),
                                  response_injections.invalid_exception_code(packet[ModbusADUResponse])]  # will need to separate randomization later on
                packet[ModbusADUResponse] = packet_choices[random.randint(0, len(packet_choices) - 1)]
                print(packet.show())

                delay += random.randint(50, 80) / 1000  # will check back with the time delay
                packet.time = packet.time + delay

                new_packets.append(packet)

            except IndexError:
                print('### request packet ###')

            # request packets
            try:
                t = packet[ModbusADURequest]

                packet.time = packet.time + delay
                #modbus_packet = packet[ModbusADURequest]
                #print('quantity', t[ModbusPDU03ReadHoldingRegistersRequest].quantity)

                new_packets.append(packet)
            except IndexError: print('### response packet ###')
        if current_protocol == 'iec104':
            if packet.haslayer(Raw):
                payload = packet[Raw].load

                if payload.startswith(b'\x68'):
                    if packet.haslayer(TCP):
                        if hack_number == '5.2':  # 5.2 Tampering with IEC APCI sequence numbers
                            chances = [0, 50, 100]; val = chances[random.randint(0, phases)]
                            packet[TCP].seq += val
                            packet[TCP].ack += val

                            if random.randint(0, 50) == 0:
                                phases = random.randint(0, len(chances)-1)

                            if TCP in packet:
                                packet = packet.__class__(bytes(packet))
                                new_checksum = packet.chksum
                                packet[TCP].chksum = new_checksum

                                new_packets.append(packet)

                        if hack_number == '5.4':  # 5.4 Packet injection
                            iec104_packet_injection.main(packet)  #  upon scapy transition, retransmission error, will look into it later on

    # needs separate field
    if hack_number == '5.4' and current_protocol == 'iec104':
        new_packets = iec104_packet_injection.packets

    scapy.utils.wrpcap(f'only_{current_protocol}_bad.pcap', new_packets)

# TODO
# import the rest of attacks for the scapy library
# everything sorted in folder, like it was previously
# more classes for readability and better structure
