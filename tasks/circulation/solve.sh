tshark -r capture.pcapng -Y "ip.checksum.status == Bad" -T fields -e ip.checksum | cut -f2 -d'x' | tr -d '\n' | xxd -r -p