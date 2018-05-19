import struct
import csv
from bitstring import BitArray

    
def ReadInt32(fileData):
    #return struct.unpack('<i', file.read(4))[0]
    return struct.unpack('>i', fileData)[0]

def ReadInt16(fileData):
    #return struct.unpack('<h', file.read(2))[0]
    return struct.unpack('>h', fileData)[0]

def ReadInt64(fileData):
    #return struct.unpack('<l', file.read(8))[0]
    return struct.unpack('>2l', fileData)[0]

def ReadUInt64(fileData):
    #return struct.unpack('<L', file.read(8))[0]
    return struct.unpack('>2L', fileData)[0]

def ReadUInt32(fileData):
    #return struct.unpack('<I', file.read(4))[0]
    return struct.unpack('>I', fileData)[0]

def ReadUInt16(fileData):
    #return struct.unpack('<H', file.read(2))[0]
    return struct.unpack('>H', fileData)[0]

def ReadSignedByte(fileData):
    #return struct.unpack('<b', file.read(1))[0]
    return struct.unpack('>b', fileData)[0]

def readUnsignedByte(fileData):
    #return struct.unpack('<B', file.read(1))[0]
    return struct.unpack('>B', fileData)[0]


def FromLVTime(unixTime, ummm):
    #var epoch = new DateTime(1904, 1, 1, 0, 0, 0, DateTimeKind.Utc);
    #epoch = epoch.AddSeconds(unixTime);
    #epoch = TimeZoneInfo.ConvertTimeFromUtc(epoch, TimeZoneInfo.Local);
    #return epoch.AddSeconds(((double)ummm / UInt64.MaxValue));
    return 0

#Trip Time is 7 bits above decimal and 1 below
def TripTimeToDouble(byte):
    return float(byte) * 0.5

#Lost packets is a byte per half second, range 0-25
#multiply by 4 to get percent loss for the period
def PacketLossToDouble(byte):
    return (float(byte) * 4) * 0.01

#Voltage is 8 bits above decimal and 8 below
def VoltageToDouble(ui16):
    return float(ui16) * 0.00390625

#CPU is 7 above, 1 below, as a percentage
def RoboRioCPUToDouble(byte):
    floatbyte = float(byte)
    return (floatbyte * 0.5) * 0.01

#flags are a byte with bits for
# robot disable, auto, tele, DS disable, auto, tele
# watchdog and brownout
def StatusFlagsToBooleanArray(byte):
    bits = BitArray(byte)
    statusFlags = [bits[0], bits[1], bits[2], bits[3], bits[4], bits[5], bits[6], bits[7]]
    return statusFlags

# CAN util is 7 above, 1 below, as a percentage
def CANUtilToDouble(byte):
    data = BitArray(byte)
    abvDc = data[0:7]
    blwDc = data[7]
    pcntAsDec = float(abvDc.int) * 0.01
    return pcntAsDec

# Signal Strength is 7 above, 1 below as dB
def WifidBToDouble(byte):
    data = BitArray(byte)
    abvDc = data[0:7]
    return (float(abvDc.int) * 0.01)

# bandwidth is 8 above, 8 below, in megaBits
def BandwidthToDouble(ui16):
    return float(ui16) * 0.00390625

def PDPValuesToArrayList(twentyBytes):
    data = BitArray(twentyBytes)
##  HOW DEAL WITH ENDIANESS???    
##    data.byteswap()
    pdpValues = []
    for pdpChnlNum in range(0, 16, 1):
        #access bitArray at pdpChnlNum * idx
        #get the 0-6 bits above-decimal bits, turn into decimal num
        bitLowIndex = 0 + (pdpChnlNum*10)
        bitHighIndex = 7 + (pdpChnlNum*10)
        bitStringAboveDecimal = data[bitLowIndex:bitHighIndex]
        #
        #get the 7-9 bits below-decimal bits, turn into decimal num
        bitLowIndex = 7 + (pdpChnlNum*10)
        bitHighIndex = 10 + (pdpChnlNum*10)
        bitStringBelowDecimal = data[bitLowIndex:bitHighIndex]
        #
        #add above-decimal number to below-decimal number divided by 1000
        pdpAmp = float(bitStringAboveDecimal.uint) + (float(bitStringBelowDecimal.uint)/1000.0)
        pdpValues.append(pdpAmp)
    return pdpValues
            
                                   

class Entry():
    def __init__(self, trip, packets, vol, rr_cpu, status_flags,
                 can, db, band, pdp, pdp_v, res, vol_s, temp,
                 time):
        self.trip_time = trip
        self.lost_packets = packets
        self.voltage = vol
        self.robo_rio_cpu = rr_cpu
        self.status_flags = status_flags
        self.brownout = status_flags[0]
        self.watchdog = status_flags[1]
        self.ds_tele = status_flags[2]
        self.ds_auto = status_flags[3]
        self.ds_disabled = status_flags[4]
        self.robot_tele = status_flags[5]
        self.robot_auto = status_flags[6]
        self.robot_disabled = status_flags[7]
        self.can_util = can
        self.wifi_db = db
        self.bandwidth = band
        self.pdp_id = pdp
        self.pdp_values = pdp_v
        self.pdp_resistance = res
        self.pdp_voltage = vol_s
        self.pdp_temperature = temp
        self.time = time




def read_log_file():
    filename= "C:/Users/Public/Documents/FRC/Log Files/2018_04_13 09_14_05 Fri.dslog"
    with open(filename, "rb") as file:
        print("opened file")
        version = ReadInt32(file.read(4))
        print(version)
        entryList = []
        if version == 3:
            print("version = 3")
            startTime = FromLVTime(ReadInt64(file.read(8)), ReadUInt64(file.read(8)))
            #
            with open('Test.csv', 'w', newline='') as csvfile:
                csvWriter = csv.writer(csvfile, delimiter=',')
                csvWriter.writerow(["time", "trip time", "packets", "voltage", "CPU usage", "brownout", "watchdog", "ds tele", "ds auto",
                                    "ds disabled", "robot tele", "robot auto", "robot disabled", "CAN usage", "wifi db", "bandwidth",
                                    "pdp id", "pdp 0", "pdp 1", "pdp 2", "pdp 3", "pdp 4", "pdp 5",
                                    "pdp 6", "pdp 7", "pdp 8", "pdp 9", "pdp 10", "pdp 11", "pdp 12", "pdp 13", "pdp 14", "pdp 15",
                                    "pdp resistance", "pdp voltage", "pdp temp"])
                #
                nextByte = file.read(1)
                while nextByte != b"":
                    trip = TripTimeToDouble(readUnsignedByte(nextByte))
                    packets = PacketLossToDouble(ReadSignedByte(file.read(1)))
                    vol = VoltageToDouble(ReadUInt16(file.read(2)))
                    rr_cpu = RoboRioCPUToDouble(readUnsignedByte(file.read(1)))
                    status_flags = StatusFlagsToBooleanArray(file.read(1))
                    brownout = status_flags[0]
                    watchdog = status_flags[1]
                    ds_tele = status_flags[2]
                    ds_auto = status_flags[3]
                    ds_disabled = status_flags[4]
                    robot_tele = status_flags[5]
                    robot_auto = status_flags[6]
                    robot_disabled = status_flags[7]
                    can = CANUtilToDouble(file.read(1))
                    db = WifidBToDouble(file.read(1))
                    bandwidth = BandwidthToDouble(ReadUInt16(file.read(2)))
                    pdp_id = readUnsignedByte(file.read(1))
                    pdp_vals_raw = file.read(21)
                    # pdp_vals = PDPValuesToArrayList(pdp_vals_raw)
                    pdp_vals_bits = BitArray(pdp_vals_raw)
                    pdp_res = readUnsignedByte(file.read(1))
                    pdp_volt = readUnsignedByte(file.read(1))
                    pdp_temp = readUnsignedByte(file.read(1))
                    time = startTime
                    #
                    startTime = (startTime + 20)
                    #20milliseconds
                    #
                    nextByte = file.read(1)
                    #
                    #entryList.append(Entry(trip, packets, vol, rr_cpu, status_flags, can, db, bandwidth,
                    #                       pdp_id, pdp_vals_raw, pdp_res, pdp_volt, pdp_temp, time))
                    #
                    pdp3 = BitArray(pdp_vals_bits[120:130])
                    print(pdp3)
                    csvWriter.writerow([time, trip, packets, vol, rr_cpu, brownout, watchdog, ds_tele, ds_auto, ds_disabled,
                                        robot_tele, robot_auto, robot_disabled, can, db, bandwidth, pdp_id,
                                        (pdp_vals_bits[150:160].uint * 0.125),
                                        (pdp_vals_bits[140:150].uint * 0.125),
                                        (pdp_vals_bits[130:140].uint * 0.125),
                                        (pdp3.uint * 0.125),
                                        (pdp_vals_bits[110:120].uint * 0.125),
                                        (pdp_vals_bits[100:110].uint * 0.125),
                                        (pdp_vals_bits[ 90:100].uint * 0.125),
                                        (pdp_vals_bits[ 80:90 ].uint * 0.125),
                                        (pdp_vals_bits[ 70:80 ].uint * 0.125),
                                        (pdp_vals_bits[ 60:70 ].uint * 0.125),
                                        (pdp_vals_bits[ 50:60 ].uint * 0.125),
                                        (pdp_vals_bits[ 40:50 ].uint * 0.125),
                                        (pdp_vals_bits[ 30:40 ].uint * 0.125),
                                        (pdp_vals_bits[ 20:30 ].uint * 0.125),
                                        (pdp_vals_bits[ 10:20 ].uint * 0.125),
                                        (pdp_vals_bits[  0:10 ].uint * 0.125),
                                        pdp_res, pdp_volt, pdp_temp])
                    #
                print("End of File")

def main():
    read_log_file()

if __name__ == "__main__":
    # execute only if run as a script
    main()
