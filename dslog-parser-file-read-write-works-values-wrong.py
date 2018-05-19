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
##    print(statusFlags)
    return statusFlags

# CAN util is 7 above, 1 below, as a percentage
def CANUtilToDouble(byte):
    data = BitArray(byte)
##    print(data.int)
    abvDc = data[0:7]
    blwDc = data[7]
##    percentage = float(abvDc.int) + (float(blwDc.int)/10)
##    print(percentage)
##    pcntAsDec = percentage * 0.01
##    print(abvDc.int)
    pcntAsDec = float(abvDc.int) * 0.01
    return pcntAsDec

# Signal Strength is 7 above, 1 below as dB
def WifidBToDouble(byte):
##    return (float(byte) * 0.5) * .01
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
##        print("bit indices: " + str(bitLowIndex) + " " + str(bitHighIndex))
        bitStringAboveDecimal = data[bitLowIndex:bitHighIndex]
##        print(str(bitStringAboveDecimal) + ", " + str(bitStringAboveDecimal.uint))
        #
        #get the 7-9 bits below-decimal bits, turn into decimal num
        bitLowIndex = 7 + (pdpChnlNum*10)
        bitHighIndex = 10 + (pdpChnlNum*10)
##        print("bit indices: " + str(bitLowIndex) + " " + str(bitHighIndex))
        bitStringBelowDecimal = data[bitLowIndex:bitHighIndex]
##        print(str(bitStringBelowDecimal) + ", " + str(bitStringBelowDecimal.uint))
        #
        #add above-decimal number to below-decimal number divided by 1000
        pdpAmp = float(bitStringAboveDecimal.uint) + (float(bitStringBelowDecimal.uint)/1000.0)
        pdpValues.append(pdpAmp)
##    for val in pdpValues:
##        print(val, end=', ')
##    print()
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
                                    "pdp id", "pdp0", "pdp1", "pdp2", "pdp3", "pdp4", "pdp5", "pdp6", "pdp7", "pdp8", "pdp9", "pdp10",
                                    "pdp11", "pdp12", "pdp13", "pdp14", "pdp15", "pdp resistance", "pdp voltage", "pdp temp"])
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
                    pdp_vals = PDPValuesToArrayList(file.read(21)) 
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
                    entryList.append(Entry(trip, packets, vol, rr_cpu, status_flags, can, db, bandwidth,
                                           pdp_id, pdp_vals, pdp_res, pdp_volt, pdp_temp, time))
                    #
                    csvWriter.writerow([time, trip, packets, vol, rr_cpu, brownout, watchdog, ds_tele, ds_auto, ds_disabled,
                                        robot_tele, robot_auto, robot_disabled, can, db, bandwidth,
                                        pdp_id, pdp_vals[0], pdp_vals[1], pdp_vals[2], pdp_vals[3], pdp_vals[4],
                                        pdp_vals[5], pdp_vals[6], pdp_vals[7], pdp_vals[8], pdp_vals[9], pdp_vals[10],
                                        pdp_vals[11], pdp_vals[12], pdp_vals[13], pdp_vals[14], pdp_vals[15],
                                        pdp_res, pdp_volt, pdp_temp])
                    #
                print("End of File")

def main():
    read_log_file()

if __name__ == "__main__":
    # execute only if run as a script
    main()
