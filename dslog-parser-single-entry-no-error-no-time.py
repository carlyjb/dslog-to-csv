import struct
from bitstring import BitArray

    
def ReadInt32(fileData):
    #return struct.unpack('<i', file.read(4))[0]
    print(fileData)
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
    print(fileData)
    print(struct.unpack('>B', fileData)[0])
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
    print(statusFlags)
    return statusFlags

# CAN util is 7 above, 1 below, as a percentage
def CANUtilToDouble(byte):
    return (float(byte) * 0.5) * .01

# Signal Strength is 7 above, 1 below as dB
def WifidBToDouble(byte):
    return (float(byte) * 0.5) * .01

# bandwidth is 8 above, 8 below, in megaBits
def BandwidthToDouble(ui16):
    return float(ui16) * 0.00390625

def PDPValuesToArrayList(twentyBytes):
    data = BitArray(twentyBytes)
##      HOW DEAL WITH ENDIANESS???    
##    data.byteswap()
    pdpValues = []
    for pdpChnlNum in range(0, 15, 1):
        #access bitArray at pdpChnlNum * idx
        #get the 0-6 bits above-decimal bits, turn into decimal num
        bitLowIndex = 0 + (pdpChnlNum*10)
        bitHighIndex = 7 + (pdpChnlNum*10)
        print("bit indices: " + str(bitLowIndex) + " " + str(bitHighIndex))
        bitStringAboveDecimal = data[bitLowIndex:bitHighIndex]
        print(str(bitStringAboveDecimal) + ", " + str(bitStringAboveDecimal.uint))
        #
        #get the 7-9 bits below-decimal bits, turn into decimal num
        bitLowIndex = 7 + (pdpChnlNum*10)
        bitHighIndex = 10 + (pdpChnlNum*10)
        print("bit indices: " + str(bitLowIndex) + " " + str(bitHighIndex))
        bitStringBelowDecimal = data[bitLowIndex:bitHighIndex]
        print(str(bitStringBelowDecimal) + ", " + str(bitStringBelowDecimal.uint))
        #
        #add above-decimal number to below decimal number divided by 100
        pdpAmp = float(bitStringAboveDecimal.uint) + (float(bitStringBelowDecimal.uint)/1000.0)
        pdpValues.append(pdpAmp)
    for val in pdpValues:
        print(val, end=', ')
        print()
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
            entryList.append(Entry(TripTimeToDouble(readUnsignedByte(file.read(1))), 
                                   PacketLossToDouble(ReadSignedByte(file.read(1))),
                                   VoltageToDouble(ReadUInt16(file.read(2))),
                                   RoboRioCPUToDouble(readUnsignedByte(file.read(1))),
                                   StatusFlagsToBooleanArray(file.read(1)),
                                   CANUtilToDouble(file.read(1)),
                                   WifidBToDouble(readUnsignedByte(file.read(1))),
                                   BandwidthToDouble(ReadUInt16(file.read(2))),
                                   readUnsignedByte(file.read(1)),
                                   PDPValuesToArrayList(file.read(21)),
                                   readUnsignedByte(file.read(1)),
                                   readUnsignedByte(file.read(1)),
                                   readUnsignedByte(file.read(1)),
                                   startTime))
            startTime = (startTime + 20)
            #20milliseconds

def main():
    read_log_file()

if __name__ == "__main__":
    # execute only if run as a script
    main()
