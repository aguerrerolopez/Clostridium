# Bruker Daltonics XMASS format

This document contains a short yet detailed description of an XMASS sample. For more information, visit:

- https://github.com/sgibb/readBrukerFlexData/wiki
- https://forgemia.inra.fr/axel.dablanc/SPRING/-/raw/main/pwiz/FlexVariableTable.xml

## File tree of a sample
Inside a sample, we only care for three files: *acqu*, *fid* and *proc*.

```
/1SLin
    /pdata/1
        /1r      SPECTRUM
        /proc    CALIBRATION_DATA
        /procs   CALIBRATION_DATA
    /acqu        ACQUISITION
    /acqu.org    ACQUISITION (with a different "$PATH" value)
    /acqus       ACQUISITION
    /acqus.org   ACQUISITION (with a different "$PATH" value)
    /fid         SPECTRUM
    /sptype      SPECTRUM_TYPE (must be "tof")
```

## Metadata to extract
Before analysis, we extract the following metadata from a sample:

| Field                                      | Variable     | File   | Example                               |
|--------------------------------------------|--------------|--------|---------------------------------------|
| Sample ID                                  | `##$ID_raw`  | *acqu* | fb60fc50-f999-42bb-a40e-0bcc5e262e1d  |
| Target ID (to group different samples)     | `##$TgIDS`   | *acqu* | G_FE4FEFFA_0C05_4941_B01DB2DEDEF2F95F |
| Acquisition date                           | `##$AQ_DATE` | *acqu* | 2023-02-22T12:48:09.692+01:00         |
| Instrument serial number                   | `##$InstrID` | *acqu* | 8604832.05252                         |
| Instrument type                            | `##$InstTyp` | *acqu* | 9                                     |
| Digitizer type                             | `##$DIGTYP`  | *acqu* | 19                                    |
| Sample position (aka "pocillo")            | `##$PATCHNO` | *acqu* | E1                                    |
| flexControl version (acquisition software) | `##$FCVer`   | *acqu* | flexControl 3.4.207.20                |
| AIDA version (calibration software)        | `##$Acquver` | *proc* | AIDA4.7.373.7                         |
| Calibration date                           | `##$CLDATE`  | *proc* | 2023-02-21T08:58:28.000+00:00         |

Some notes about this data:

- Instrument type 9 is "microflex"
- Digitizer type 19 is "Bruker BD0G5"
