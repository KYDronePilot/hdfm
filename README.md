# HDFM - HD Radio GUI

View live data collected from HD Radio stations

![App window](img/main_screen.png)

## Features

Uses [NRSC-5](https://github.com/theori-io/nrsc5) with an [RTL-SDR dongle](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) to display live data captured from HD Radio stations

Blazing fast, fully native Rust GUI application

GUI is styled like a digital car stereo system, displaying:

- Traffic map
- Weather radar
- Station/artist artwork
- Other station/song metadata

Requires no internet connection, so it can be used off the grid

## Installation

### macOS

```bash
curl -sSL https://raw.githubusercontent.com/hdfm/hdfm/master/install.sh > /usr/local/bin/hdfm
```

### Windows

```powershell
curl -sSL https://raw.githubusercontent.com/hdfm/hdfm/master/install.sh > /usr/local/bin/hdfm
```

### Linux

**Note**: You must have Vulcan graphics installed to run on Linux.

```bash
curl -sSL https://raw.githubusercontent.com/hdfm/hdfm/master/install.sh > /usr/local/bin/hdfm
```

## Usage

**Note**: [nrsc5](https://github.com/theori-io/nrsc5) must already be installed for hdfm to run.

After installing, run `hdfm --help` to view parameters and usage.

## Souce code access

This project is released as "Pay-source" software. Precompiled binaries are provided under the [Releases](https://github.com/KYDronePilot/hdfm/releases) page for anyone to use.

If you would like to access the source code, please pay a one-time fee of $20 though GitHub Sponsors. You will then be given access to the private repository containing the code. With this access, you have permission to:

- Fork/clone and make modifications
- Build and distribute your own binaries
- Contribute back to the project and official binaries

You will not be permitted to distribute/publish the original and/or modified versions of the source code.

### [Click here to get source code access](https://github.com/sponsors/KYDronePilot/sponsorships?sponsor=KYDronePilot&tier_id=208482)

## Compatible radio stations

A list of nearby HD Radio stations can be found at: <https://hdradio.com/stations>

In addition, the station must be operated by iHeartRadio to access weather and traffic data. A list of iHeartRadio-owned stations in the US can be found here: <https://en.wikipedia.org/wiki/List_of_radio_stations_owned_by_iHeartMedia>

## Requirements

- An [rtl-sdr dongle](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/)
- The [nrsc5 program](https://github.com/theori-io/nrsc5)

## Copyright

Copyright (c) 2022 Michael Galliers. All Rights Reserved.
