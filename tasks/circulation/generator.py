#!/usr/bin/env python3

import dpkt
import random
import os.path
from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag

RUMEGATIK_IP = b'\xc1\x8a\x59\x28'
RUMEGATIK_PACKETS_NUM = 272

def process_flag(flag):
    flag = flag.encode('utf-8').hex()
    if len(flag) % 4 != 0:
        flag += '20'
    flag = [flag[i:i+4] for i in range(0, len(flag), 4)]
    return flag

def read_pcap(file):
    with open(file, 'rb') as f:
        pcap = dpkt.pcapng.Reader(f)
        packets = pcap.readpkts()
        return packets

def write_pcap(pcap, flag, positions):
    location = os.path.join(get_attachments_dir(), "capture.pcapng")

    with open(location, 'wb') as out:
        output = dpkt.pcapng.Writer(out)
        pos = 0
        megatik_pkt_counter = 0
      
        for i in range(len(pcap)):
            ts = pcap[i][0]
            buf = pcap[i][1]
            
            eth = dpkt.ethernet.Ethernet(buf)
            if not isinstance(eth.data, dpkt.ip.IP):
                output.writepkt(buf, ts)
                continue
            
            ip = eth.data
            if ip.src == RUMEGATIK_IP:
                if pos < len(flag) and megatik_pkt_counter == positions[pos]:
                    payload = int(flag[pos], 16)
                    if ip.sum == payload:
                        return True
                    ip.sum = payload
                    pos += 1
                megatik_pkt_counter += 1
                eth.data = ip
                output.writepkt(bytes(eth), ts)
            else:
                output.writepkt(buf, ts)
        return False

def get_positions(flag_length):
    positions = random.sample(range(RUMEGATIK_PACKETS_NUM), flag_length)
    positions.sort()
    return positions

def generate():
    flag = process_flag(get_flag())
    packets = read_pcap("base.pcapng")
    result = True
    while(result):
        positions = get_positions(len(flag))
        result = write_pcap(packets, flag, positions)

if __name__ == "__main__":
    generate()