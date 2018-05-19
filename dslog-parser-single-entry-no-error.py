import struct
#from bitstring import BitArray

    
def ReadInt32():
    return struct.unpack('<i', file.read(4))[0]

def ReadInt16():
    return struct.unpack('<h', file.read(2))[0]

def ReadInt64():
    return struct.unpack('<l', file.read(8))[0]

def ReadUInt64():
    return struct.unpack('<L', file.read(8))[0]

def ReadUInt32():
    return struct.unpack('<I', file.read(4))[0]

def ReadUInt16():
    return struct.unpack('<H', file.read(2))[0]

def ReadSignedByte():
    return struct.unpack('<b', file.read(1))[0]

def readUnsignedByte():
    return struct.unpack('<B', file.read(1))[0]


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
def PacketLossToDouble(sbyte):
    return float(byte * 4) * 0.01

#Voltage is 8 bits above decimal and 8 below
def VoltageToDouble(ui16):
    return float(ui16) * 0.00390625

#CPU is 7 above, 1 below, as a percentage
def RoboRioCPUToDouble(byte):
    return (float(byte) * 0.5) * 0.01

#flags are a byte with bits for
# robot disable, auto, tele, DS disable, auto, tele
# watchdog and brownout
def StatusFlagsToBooleanArray(byte):
    byteArray = { byte };
    return byteArray.SelectMany(GetBits).ToArray()

# CAN util is 7 above, 1 below, as a percentage
def CANUtilToDouble(byte):
    return (float(byte) * 0.5) * .01

# Signal Strength is 7 above, 1 below as dB
def WifidBToDouble(byte):
    return (float(byte) * 0.5) * .01

# bandwidth is 8 above, 8 below, in megaBits
def BandwidthToDouble(ui16):
    return float(ui16) * 0.00390625

def getBits(byteArray):
    for b in byteArray:
        #reversed for Big Endian
        for idx in reversed(xrange(8)):
            yield (b >> idx) & 1

def PDPValuesToArrayList(twentyByteArray):
    bitArray = getBits(twentyByteArray)
    pdpValues = []
    for pdpChnlNum in xrange(0, 15, 1):
        #access bitArray at pdpChnlNum * idx
        #get the 0-6 bits above-decimal bits, turn into decimal num
        charsAD = []
        charsAD.append(chr(int(''.join([str(bit) for bit in bitArray[(0+(pdpChnlNum*10)):(7+(pdpChnlNum*10))]], 2))))
        bitStringAboveDecimal = ''.join(charsAD)
        #get the 7-9 bits below-decimal bits, turn into decimal num
        charsBD = []
        charsBD.append(chr(int(''.join([str(bit) for bit in bitArray[(7+(pdpChnlNum*10)):(10+(pdpChnlNum*10))]], 2))))
        bitStringBelowDecimal = ''.join(charsBD)
        #add above-decimal number to below decimal number divided by 100
        pdpAmp = float(int(bitStringAboveDecimal)) + float(int(bitStringBelowDecimal)/1000)
        pdpValues.push(pdpAmp)
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


entryList = [];

def read_log_file():
    filename= "C:/Users/Public/Documents/FRC/Log\ Files/2018_04_13 09_14_05 Fri.dslog"
    with open(filename, "rb") as file:
        version = ReadInt32()
        if version == 3:
            startTime = FromLVTime(ReadInt64(), ReadUInt64())
            entryList.append(Entry(TripTimeToDouble(reader.ReadByte()), 
                                       PacketLossToDouble(reader.ReadSByte()),
                                       VoltageToDouble(reader.ReadUInt16()),
                                       RoboRioCPUToDouble(reader.ReadByte()),
                                       StatusFlagsToBooleanArray(reader.ReadByte()),
                                       CANUtilToDouble(reader.ReadByte()),
                                       WifidBToDouble(reader.ReadByte()),
                                       BandwidthToDouble(reader.ReadUInt16()),
                                       reader.ReadByte(),
                                       PDPValuesToArrayList(reader.ReadBytes(21)),
                                       reader.ReadByte(),
                                       reader.ReadByte(),
                                       reader.ReadByte(),
                                       StartTime.AddMilliseconds(20)))

            
