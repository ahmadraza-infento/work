import time
import socket
import pickle
from threading import Thread
from random import randint

class UDPClient():
    """ module to enable client's communication with server  """
    def __init__(self, destination, stream=True):
        """ class constructor
        """
        super().__init__()
        self._client        = None   
        self._seq_number    = randint(0, 2048)
        self._byte_len      = 640 # bits
        self._destination   = destination
        self._stop          = False
        self._queue         = []
        self._busy          = False

        if stream:
            self._th = Thread(target=self._streamed_sending)
            self._th.setDaemon(True)
            self._th.start()

    @property
    def seq_number(self):
        self._seq_number += 1
        return self._seq_number         

    #region Generate Packet
    def _generate_rtp_packet(self, rtp_params):

        version = str(format(rtp_params['version'], 'b').zfill(2))                  #RFC189 Version (Typically 2)
        padding = str(rtp_params['padding'])                                        #Padding (Typically false (0))
        extension = str(rtp_params['extension'])                                    #Extension - Disabled
        csi_count = str(format(rtp_params['csi_count'], 'b').zfill(4))              #Contributing Source Identifiers Count (Typically 0)
        byte1 = format(int((version + padding + extension + csi_count), 2), 'x').zfill(2)                           #Convert binary values to an int then format that as hex with 2 bytes of padding if requiredprint(byte1)

        #Generate second byte of header as binary string:
        marker = str(rtp_params['marker'])                                          #Marker (Typically false)
        payload_type = str(format(rtp_params['payload_type'], 'b').zfill(7))        #7 bit Payload Type (From https://tools.ietf.org/html/rfc3551#section-6)
        byte2 = format(int((marker + payload_type), 2), 'x').zfill(2)               #Convert binary values to an int then format that as hex with 2 bytes of padding if required

        sequence_number = format(rtp_params['sequence_number'], 'x').zfill(4)                               #16 bit sequence number (Starts from a random position and incriments per packet)
        
        timestamp = format(rtp_params['timestamp'], 'x').zfill(8)                   #(Typically incrimented by the fixed time between packets)
        
        ssrc = str(format(rtp_params['ssrc'], 'x').zfill(8))                        #SSRC 32 bits           (Typically randomly generated for each stream for uniqueness)

        payload = rtp_params['payload']
        print(type(byte1), type(byte2), type(sequence_number), type(timestamp), type(ssrc), type(payload) )
        packet = byte1 + byte2 + sequence_number + timestamp + ssrc + payload
        return packet

    def _rtp_packet(self, packet_args):
        return pickle.dumps(packet_args)

    def _seq_packet(self, data):
        """ generate packet with sequence_number & payload """
        return pickle.dumps({"sequence_number":self.seq_number, "payload":data})
    #endregion
    
    #region Send Packet
    def send_rtp(self, data):
        if self._busy:
            self._queue.append(data)
        
        else:
            self._busy = True
            payload = str(pickle.dumps(data))
            packet_vars = {'version' : 2, 'padding' : 0, 'extension' : 0, 'csi_count' : 0, 
                            'marker' : 0, 'payload_type' : 8, 'sequence_number' : self.seq_number, 
                            'timestamp' : self.seq_number, 'ssrc' : 185755418, 
                            'payload' : payload} 
            rtp_hex = self._generate_rtp_packet(packet_vars)
            bytedata= bytes.fromhex(rtp_hex)
            while len(bytedata) > 0:
                data_to_sent = bytedata[:self._byte_len]
                self._client.sendto( data_to_sent, self._destination )
                bytedata = bytedata[self._byte_len:]
            
            self._client.sendto( b"__end__", self._destination )

            if len(self._queue) > 0:
                self._busy = False
                self.send( self._queue.pop(0) )

    def send(self, data):
        if self._busy is True:
            self._queue.append(data)
        
        else:
            self._busy = True
            bytedata = pickle.dumps(data)
            while len(bytedata) > 0:
                data_to_sent = bytedata[:self._byte_len]
                self._client.sendto( data_to_sent, self._destination )
                bytedata = bytedata[self._byte_len:]
            
            self._client.sendto( b"__end__", self._destination )

            if len(self._queue) > 0:
                self._busy = False
                self.send( self._queue.pop(0) )
            else:
                self._busy = False

    def _streamed_sending(self):
        """ Send Queue data in stream """
        while self._stop is False:
            try:
                packet  = self._queue.pop(0)
                while len(packet) > 0:
                    data_to_sent        = packet[:self._byte_len]
                    self._client.sendto ( data_to_sent, self._destination )
                    resp                = self._client.recv(64)
                    if resp == b"__ack__":
                        packet  = packet[self._byte_len:]
                
                self._client.sendto( b"__end__", self._destination )
            
            except Exception as e:
                pass
    #endregion

    #region Push Queue
    def push_seq(self, data):
        packet = self._seq_packet(data)
        self._queue.append(packet)

    def push(self, data):
        self._queue.append(pickle.dumps(data))
    #endregion
    
    def connect(self, ip='127.0.0.1', port=12000):
        try:
            self._client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            self._client.bind((ip, port))

        except Exception as e:
            print("exception@connect:", e)
            self._client = None

    def stop(self):
        self._stop = True

    def close(self):
        """ close session with server """
        self._client.close()   

    


# main code to run client
if __name__ == '__main__':
    server_ip   = '127.0.0.1'  
    server_port = 12000
    client      = UDPClient( (server_ip, server_port) )
    client.connect()
