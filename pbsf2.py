import os
import sys
import struct
import wave
import audioop

def get_u32_be(buf, off=0):
    return struct.unpack(">I", buf[off:off+4])[0]

def get_u16_be(buf, off=0):
    return struct.unpack(">H", buf[off:off+2])[0]

def get_u8(buf, off=0):
    return struct.unpack("B", buf[off:off+1])[0]

def main(argc=len(sys.argv), argv=sys.argv):
    if argc != 2 or not os.path.isfile(argv[1]):
        print("Usage: %s file.wt" % argv[0])
        return 1

    os.chdir( os.path.dirname( os.path.realpath( argv[1] ) ) )

    wt_name = os.path.splitext( os.path.basename(argv[1]) )[0]

    with open("%s.wt" % wt_name, "rb") as wt:
        wtbuf = wt.read()

    header_size = get_u32_be(wtbuf, 0x00)

    tb1_offset = get_u32_be(wtbuf, 0x04)
    tb2_offset = get_u32_be(wtbuf, 0x08)
    tb3_offset = get_u32_be(wtbuf, 0x0C)
    tb4_offset = get_u32_be(wtbuf, 0x10)
    tb5_offset = get_u32_be(wtbuf, 0x14)

    with open("%s_sfubar.txt" % wt_name, "w") as txt:
        #
        # mandatory header stuff
        #
        txt.write("RIFF.LIST.isng.zstr=EMU8000\n")
        txt.write("RIFF.LIST.INAM.zstr=%s\n" % wt_name)

        #
        # extract samples and write the wavetable list
        #
        sampmap = {
        }

        with open("%s.pcm" % wt_name, "rb") as pcm:

            num_entries = (tb5_offset - tb4_offset) // 16
            tmp_offset = tb4_offset

            for i in range(num_entries):

                channels    = get_u16_be(wtbuf, tmp_offset+0x00)
                sample_rate = get_u16_be(wtbuf, tmp_offset+0x02)
                offset      = get_u32_be(wtbuf, tmp_offset+0x04)
                size        = get_u32_be(wtbuf, tmp_offset+0x08)
                sample_id   = get_u16_be(wtbuf, tmp_offset+0x0C)

                sidx = 1 + i

                sampmap[sample_id] = sidx

                pcm.seek(offset * 2)

                wav_path = "%s_%02d.wav" % (wt_name, sample_id)

                with wave.open(wav_path, "wb") as wav:
                    wav.setnchannels(channels)
                    wav.setsampwidth(2)
                    wav.setframerate(sample_rate)
                    bepcm = pcm.read(size * 2)
                    lepcm = audioop.byteswap(bepcm, 2)
                    wav.writeframes(lepcm)

                txt.write("SF2.wt.%d.wav=%s\n" % (sidx, wav_path))

                tmp_offset += 16

        #
        # get zone info
        #
        tmp_offset = tb2_offset
        num_entries = (tb3_offset - tb2_offset) // 24
        zoneinfo = {}
        for i in range(num_entries):
            basenote     = get_u8(wtbuf, tmp_offset+0x00)
            #loop_start  = get_u32_be(wtbuf, tmp_offset+0x08)
            #loop_length = get_u32_be(wtbuf, tmp_offset+0x0C)
            zoneid       = get_u16_be(wtbuf, tmp_offset+0x12)
            sample_id    = get_u16_be(wtbuf, tmp_offset+0x16)

            zoneinfo[zoneid] = {
                "sample_id": sample_id,
                "basenote": basenote,
            }

            tmp_offset += 24

        #
        # write instrument info
        #
        tmp_offset = tb1_offset
        table = 0
        instrument = 1
        presetbuffer = ""
        while table < 16:

            if wtbuf[tmp_offset:tmp_offset+0x100] != b"\xFF\xFF" * 128:

                txt.write("SF2.in.%d.name=Instrument%02d\n" % (instrument, instrument))

                key = 0

                zoneIndex = 1

                while key < 128:

                    destZoneId = get_u16_be(wtbuf, tmp_offset)

                    loKey = key

                    while key < 128:
                        thisZoneId = get_u16_be(wtbuf, tmp_offset)

                        if thisZoneId == destZoneId:
                            hiKey = key
                        else:
                            break

                        key += 1

                        tmp_offset += 2

                    basenote = zoneinfo[destZoneId]["basenote"]
                    sample_id = zoneinfo[destZoneId]["sample_id"]

                    txt.write("SF2.in.%d.zone.%d.keyRange=%d,%d\n" % (instrument, zoneIndex, loKey, hiKey))
                    txt.write("SF2.in.%d.zone.%d.overridingRootKey=%d\n" % (instrument, zoneIndex, basenote))
                    txt.write("SF2.in.%d.zone.%d.wt=%d\n" % (instrument, zoneIndex, sampmap[sample_id]))

                    zoneIndex += 1

                # add generic preset info
                presetbuffer += "SF2.ps.%d.name=Preset%02d\n" % (instrument, instrument)
                presetbuffer += "SF2.ps.%d.bank=0\n" % instrument
                presetbuffer += "SF2.ps.%d.zone.1.keyRange=0,127\n" % instrument
                presetbuffer += "SF2.ps.%d.zone.1.in=%d\n" % (instrument, instrument)

                instrument += 1

            else:

                tmp_offset += 256

            table += 1


        #
        # write preset info
        #
        txt.write(presetbuffer)


if __name__=="__main__":
    main()