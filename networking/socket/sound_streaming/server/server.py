import pickle
import socket
import sounddevice as sd
from threading import Thread

class StreamPlayer(Thread):
    def __init__(self, ) -> None:
        super().__init__()
        self._stop  = False
        self._queue = []

    def add_data(self, data):
        self._queue.append(data)

    def run(self) -> None:
        while self._stop is False:
            try:
                data = self._queue.pop(0)
                sd.play(data, 44100)
                sd.sleep(1000)
            except:
                pass
    
    def stop_work(self):
        self._stop = True
        self._queue.clear()

            
class Server(Thread):

    def __init__(self, host="127.0.0.1", port=19000):
        """ initialize server using socket module
            >>> @param:host -> ip address for server
            >>> @param:port -> port to open by server to receive client request
        """
        
        super().__init__()
        self.host       = host
        self.port       = port
        self.server     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bytes_len = 640
        self._stop      = False
        self._data_received = None
        self._stream_player = None

    #region decode packet
    def _decode_rtp_packet(self, packet_bytes):
        packet_vars             = {}
        byte1                   = packet_bytes[0:2]           #Byte1 as Hex
        byte1                   = int(byte1, 16)              #Convert to Int
        byte1                   = format(byte1, 'b')          #Convert to Binary
        packet_vars['version']  = int(byte1[0:2], 2)     #Get RTP Version
        packet_vars['padding']  = int(byte1[2:3])        #Get padding bit
        packet_vars['extension']= int(byte1[3:4])        #Get extension bit
        packet_vars['csi_count']= int(byte1[4:8], 2)     #Get RTP Version

        byte2                   = packet_bytes[2:4]

        byte2                   = int(byte2, 16)              #Convert to Int
        byte2                   = format(byte2, 'b').zfill(8) #Convert to Binary
        packet_vars['marker']   = int(byte2[0:1])
        packet_vars['payload_type'] = int(byte2[1:8], 2)

        packet_vars['sequence_number']  = int(str(packet_bytes[4:8]), 16)

        packet_vars['timestamp']= int(str(packet_bytes[8:16]), 16)

        packet_vars['ssrc']     = int(str(packet_bytes[16:24]), 16)

        packet_vars['payload']  = str(packet_bytes[24:])
        return packet_vars
    
    #endregion
    
    #region receive
    def _receive_stream(self):
        """ receive a data stream """
        while self._stop is False:
            data, addr = self.server.recvfrom(self._bytes_len)
            if data == b"__end__":
                packet  = pickle.loads(self._data_received)
                seq_num = packet['sequence_number']
                payload = packet['payload']
                print("received -> ", seq_num, type(payload), payload.shape)
                self._data_received = None
                if self._stream_player:
                    self._stream_player.add_data(payload)
            else:
                self._data_received = data if self._data_received is None else self._data_received+data
                self.server.sendto(b"__ack__", addr)
    #endregion
    
    def set_stream_player(self, value):
        self._stream_player = value

    def stop_work(self):
        self._stop = True

    def _bind(self):
        """ bind server with provided host and port"""
        self.server.bind((self.host, self.port))

    def _listen(self):
        """ start listening for client requests """
        print(f"Listening at {self.host}/{self.port} ")   
    
    def _accept_clients(self):
        """ accept client request and start ClientInterface for individual client """
        self._receive_stream()

    def run(self):
        """ entr point for server module """
        self._bind()
        self._listen()
        self._accept_clients()
        
# main execution
if __name__ == '__main__':
    server = Server()
    stream_player = StreamPlayer()
    stream_player.setDaemon(True)
    server.setDaemon(True)

    server.set_stream_player(stream_player)
    server.start()
    stream_player.start()

    _ = input("press enter to exit!")
    server.stop_work()
    stream_player.stop_work()

