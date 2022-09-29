import sounddevice as sd
from client import UDPClient

def main():
    c           = UDPClient( destination=("127.0.0.1", 19000) )
    c.connect   ()
    
    def callback(indata, outdata, frames, time, status):
        #outdata[:] = indata
        print("sending -> ", indata.shape)
        c.push_seq(indata)

    with sd.Stream(channels=2, samplerate=44100, callback=callback):
        while True:
            sd.sleep(int(5*1000))

    c.stop()

if __name__ == "__main__":
    main()