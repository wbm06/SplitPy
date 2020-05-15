# Copyright 2019 Pascal Audet & Andrew Schaeffer
#
# This file is part of SplitPy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""

Module containing the main utility functions used in the `SplitPy` scripts
that accompany this package.

"""

# -*- coding: utf-8 -*-
from obspy import UTCDateTime
from numpy import nan, isnan


def get_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script wrapping "
        "together the python-based implementation of SplitLab by " +
        "Wustefeld and others. This version " +
        "requests data on the fly for a given date range. Data is " +
        "requested from the internet using " +
        "the client services framework or from data provided on a " +
        "local disk. The stations are processed " +
        "one by one with the SKS Splitting parameters measured " +
        "individually using both the " +
        "Rotation-Correlation (RC) and Silver & Chan (SC) methods.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type="string",
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys " +
        "will be used to match against those in the " +
        "dictionary. For instance, providing IU will match with " +
        "all stations in the IU network [Default processes " +
        "all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing Split results. " +
        "Default behaviour prompts for those that " +
        "already exist. Selecting overwrite and skip (ie, both flags) " +
        "negate each other, and both are set to " +
        "false (every repeat is prompted). [Default False]")
    parser.add_option(
        "-K", "--skip-existing",
        action="store_true",
        dest="skip",
        default=False,
        help="Skip any event for which existing splitting results are " +
        "saved to disk. Default behaviour prompts for " +
        "each event. Selecting skip and overwrite (ie, both flags) " +
        "negate each other, and both are set to " +
        "False (every repeat is prompted). [Default False]")

    # Server Settings
    ServerGroup = OptionGroup(
        parser,
        title="Server Settings",
        description="Settings associated with which " +
        "datacenter to log into.")
    ServerGroup.add_option(
        "-S", "--Server",
        action="store",
        type=str,
        dest="Server",
        default="IRIS",
        help="Specify the server to connect to. Options include: " +
        "BGR, ETH, GEONET, GFZ, INGV, IPGP, IRIS, KOERI, LMU, NCEDC, " +
        "NEIP, NERIES, ODC, ORFEUS, RESIF, SCEDC, USGS, USP. [Default IRIS]")
    ServerGroup.add_option(
        "-U", "--User-Auth",
        action="store",
        type=str,
        dest="UserAuth",
        default="",
        help="Enter your IRIS Authentification Username and Password " +
        "(--User-Auth='username:authpassword') to access and download " +
        "restricted data. [Default no user and password]")

    # Database Settings
    DataGroup = OptionGroup(
        parser,
        title="Local Data Settings",
        description="Settings associated with defining and using a " +
        "local data base of pre-downloaded day-long SAC files.")
    DataGroup.add_option(
        "--local-data",
        action="store",
        type="string",
        dest="localdata",
        default=None,
        help="Specify a comma separated list of paths containing " +
        "day-long sac files of data already downloaded. " +
        "If data exists for a seismogram is already present on " +
        "disk, it is selected preferentially over downloading " +
        "the data using the Client interface")
    DataGroup.add_option(
        "--no-data-zero",
        action="store_true",
        dest="ndval",
        default=False,
        help="Specify to force missing data to be set as zero, rather " +
        "than default behaviour which sets to nan.")
    DataGroup.add_option(
        "--no-local-net",
        action="store_false",
        dest="useNet",
        default=True,
        help="Specify to prevent using the Network code in the " +
        "search for local data (sometimes for CN stations " +
        "the dictionary name for a station may disagree with that " +
        "in the filename. [Default Network used]")

    # Constants Settings
    ConstGroup = OptionGroup(
        parser,
        title='Parameter Settings',
        description="Miscellaneous default values and settings")
    ConstGroup.add_option(
        "--Vp",
        action="store",
        type="float",
        dest="vp",
        default=6.,
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option(
        "--SNR",
        action="store",
        type="float",
        dest="msnr",
        default=7.5,
        help="Specify the SNR threshold used to determine whether " +
        "events are processedc. [Default 7.5]")
    ConstGroup.add_option(
        "--window",
        action="store",
        type="float",
        dest="dts",
        default=120.,
        help="Specify time window length before and after the SKS "
        "arrival. The total window length is 2*dst. [Default 120 s]")
    ConstGroup.add_option(
        "--max-delay",
        action="store",
        type="float",
        dest="maxdt",
        default=4.,
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option(
        "--time-increment",
        action="store",
        type="float",
        dest="ddt",
        default=0.1,
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option(
        "--angle-increment",
        action="store",
        type="float",
        dest="dphi",
        default=1.,
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option(
        "--transverse-SNR",
        action="store",
        type="float",
        dest="snrTlim",
        default=1.,
        help="Specify the minimum SNR Threshold for the Transverse " +
        "component to be considered Non-Null. [Default 1.]")

    # Event Selection Criteria
    EventGroup = OptionGroup(
        parser,
        title="Event Settings",
        description="Settings associated with refining "
        "the events to include in matching station pairs")
    EventGroup.add_option(
        "--start-time",
        action="store",
        type="string",
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the start time for the event search. This will override any " +
        "station start times. [Default start date of each station]")
    EventGroup.add_option(
        "--end-time",
        action="store",
        type="string",
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the end time for the event search. This will override any " +
        "station end times [Default end date of each station]")
    EventGroup.add_option(
        "--reverse-order", "-R",
        action="store_true",
        dest="reverse",
        default=False,
        help="Reverse order of events. Default behaviour starts at " +
        "oldest event and works towards most recent. " +
        "Specify reverse order and instead the program will start " +
        "with the most recent events and work towards older")
    EventGroup.add_option(
        "--min-mag",
        action="store",
        type="float",
        dest="minmag",
        default=6.0,
        help="Specify the minimum magnitude of event for which to " +
        "search. [Default 6.0]")
    EventGroup.add_option(
        "--max-mag",
        action="store",
        type="float",
        dest="maxmag",
        default=None,
        help="Specify the maximum magnitude of event for which to " +
        "search. [Default None, i.e. no limit]")

    # Geometry Settings
    GeomGroup = OptionGroup(
        parser,
        title="Geometry Settings",
        description="Settings associatd with the "
        "event-station geometries")
    GeomGroup.add_option(
        "--min-dist",
        action="store",
        type="float",
        dest="mindist",
        default=85.,
        help="Specify the minimum great circle distance (degrees) " +
        "between the station and event. [Default 85]")
    GeomGroup.add_option(
        "--max-dist",
        action="store",
        type="float",
        dest="maxdist",
        default=120.,
        help="Specify the maximum great circle distance (degrees) " +
        "between the station and event. [Default 120]")

    parser.add_option_group(ServerGroup)
    parser.add_option_group(DataGroup)
    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " +
                opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " +
                opts.endT)
    else:
        opts.endT = None

    # Parse User Authentification
    if not len(opts.UserAuth) == 0:
        tt = opts.UserAuth.split(':')
        if not len(tt) == 2:
            parser.error(
                "Error: Incorrect Username and Password Strings for " +
                "User Authentification")
        else:
            opts.UserAuth = tt
    else:
        opts.UserAuth = []

    # Check existing file behaviour
    if opts.skip and opts.ovr:
        opts.skip = False
        opts.ovr = False

    # Parse Local Data directories
    if opts.localdata is not None:
        opts.localdata = opts.localdata.split(',')
    else:
        opts.localdata = []

    # Check NoData Value
    if opts.ndval:
        opts.ndval = 0.0
    else:
        opts.ndval = nan

    return (opts, indb)


def get_options_prep():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for preparation of SKS data for offline processing

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script to " +
        "download and prepare datasets for SKS splitting processing. " +
        "This script downloads and prepares event and station data, " +
        "so that splitting can then be calculated offline.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type="string",
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for which " +
        "to perform analysis. These must be contained within the " +
        "station database. Partial keys will be used to match against " +
        "those in the dictionary. For instance, providing IU will match " +
        "with all stations in the IU network [Default " +
        "processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "--local-data",
        action="store",
        type="string",
        dest="localdata",
        default=None,
        help="Specify a comma separated list of paths containing " +
        "day-long sac files of data already downloaded. If data exists " +
        "for a seismogram is already present on disk, it is selected " +
        "preferentially over downloading the data using the Client interface")
    parser.add_option(
        "--no-data-zero",
        action="store_true",
        dest="ndval",
        default=False,
        help="Specify to force missing data to be set as zero, rather " +
        "than default behaviour which sets to nan.")
    parser.add_option(
        "--no-local-net",
        action="store_false",
        dest="useNet",
        default=True,
        help="Specify to prevent using the Network code in the search " +
        "for local data (sometimes for CN stations the dictionary name " +
        "for a station may disagree with that in the filename. " +
        "[Default Network used]")
    parser.add_option(
        "-D", "--data-directory",
        action="store",
        type="string",
        dest="datadir",
        default="DATA",
        help="Specify the directory prefix in which the prepared data " +
        "is stored. [Default 'DATA']. The start and end time and date " +
        "as well as min and max magnitudes are included in the final " +
        "folder name.")

    # Server Settings
    ServerGroup = OptionGroup(
        parser,
        title="Server Settings",
        description="Settings associated with which "
        "datacenter to log into.")
    ServerGroup.add_option(
        "-S", "--Server",
        action="store",
        type=str,
        dest="Server",
        default="IRIS",
        help="Specify the server to connect to. Options include: " +
        "BGR, ETH, GEONET, GFZ, INGV, IPGP, IRIS, KOERI, LMU, NCEDC, " +
        "NEIP, NERIES, ODC, ORFEUS, RESIF, SCEDC, USGS, USP. [Default IRIS]")
    ServerGroup.add_option(
        "-U", "--User-Auth",
        action="store",
        type=str,
        dest="UserAuth",
        default="",
        help="Enter your IRIS Authentification Username and Password " +
        "(--User-Auth='username:authpassword') to access and download " +
        "restricted data. [Default no user and password]")

    # Constants Settings
    ConstGroup = OptionGroup(
        parser,
        title='Parameter Settings',
        description="Miscellaneous default values and settings")
    ConstGroup.add_option(
        "--Vp",
        action="store",
        type="float",
        dest="vp",
        default=6.,
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option(
        "--SNR",
        action="store",
        type="float",
        dest="msnr",
        default=7.5,
        help="Specify the SNR threshold used to determine whether " +
        "events are processedc. [Default 7.5]")
    ConstGroup.add_option(
        "--window",
        action="store",
        type="float",
        dest="dts",
        default=120.,
        help="Specify time window length before and after the " +
        "SKS arrival. The total window length is "
        "2*dst. [Default 120 s]")
    ConstGroup.add_option(
        "--max-delay",
        action="store",
        type="float",
        dest="maxdt",
        default=4.,
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option(
        "--time-increment",
        action="store",
        type="float",
        dest="ddt",
        default=0.1,
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option(
        "--angle-increment",
        action="store",
        type="float",
        dest="dphi",
        default=1.,
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option(
        "--transverse-SNR",
        action="store",
        type="float",
        dest="snrTlim",
        default=1.,
        help="Specify the minimum SNR Threshold for the Transverse " +
        "component to be considered Non-Null. [Default 1.]")

    # Event Selection Criteria
    EventGroup = OptionGroup(
        parser,
        title="Event Settings",
        description="Settings associated with "
        "refining the events to include in matching station pairs")
    EventGroup.add_option(
        "--start-time",
        action="store",
        type="string",
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing the " +
        "start time for the event search. This will override any station " +
        "start times. [Default more recent start date for each station pair]")
    EventGroup.add_option(
        "--reverse-order", "-R",
        action="store_true",
        dest="reverse",
        default=False,
        help="Reverse order of events. Default behaviour starts at " +
        "oldest event and works towards most " +
        "recent. Specify reverse order and instead the program will " +
        "start with the most recent events and "
        "work towards older")
    EventGroup.add_option(
        "--end-time",
        action="store",
        type="string",
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the end time for the event search. " +
        "This will override any station end times [Default older end " +
        "date for each the pair of stations]")
    EventGroup.add_option(
        "--min-mag",
        action="store",
        type="float",
        dest="minmag",
        default=6.0,
        help="Specify the minimum magnitude of event for which to " +
        "search. [Default 6.0]")
    EventGroup.add_option(
        "--max-mag",
        action="store",
        type="float",
        dest="maxmag",
        default=None,
        help="Specify the maximum magnitude of event for which to " +
        "search. [Default None, ie no limit]")

    # Geometry Settings
    GeomGroup = OptionGroup(
        parser,
        title="Geometry Settings",
        description="Settings associatd with the "
        "event-station geometries")
    GeomGroup.add_option(
        "--min-dist",
        action="store",
        type="float",
        dest="mindist",
        default=85.,
        help="Specify the minimum great circle distance (degrees) " +
        "between the station and event. [Default 85]")
    GeomGroup.add_option(
        "--max-dist",
        action="store",
        type="float",
        dest="maxdist",
        default=120.,
        help="Specify the maximum great circle distance (degrees) " +
        "between the station and event. [Default 120]")

    parser.add_option_group(ServerGroup)
    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " +
                opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " +
                opts.endT)
    else:
        opts.endT = None

    # Parse User Authentification
    if not len(opts.UserAuth) == 0:
        tt = opts.UserAuth.split(':')
        if not len(tt) == 2:
            parser.error(
                "Error: Incorrect Username and Password Strings " +
                "for User Authentification")
        else:
            opts.UserAuth = tt
    else:
        opts.UserAuth = []

    # Parse Local Data directories
    if opts.localdata is not None:
        opts.localdata = opts.localdata.split(',')
    else:
        opts.localdata = []

    # Check NoData Value
    if opts.ndval:
        opts.ndval = 0.0
    else:
        opts.ndval = nan

    return (opts, indb)


def get_options_offline():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for processing SKS data offline 

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script to process "
        "and calculate the spliting parmaters for a dataset " +
        "that has already been downloaded by sks_prep.py. ")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type="string",
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys " +
        "for which to perform analysis. These must be " +
        "contained within the station database. Partial keys " +
        "will be used to match against those in the " +
        "dictionary. For instance, providing IU will match " +
        "with all stations in the IU network [Default " +
        "processes all stations in the database]")

    # Constants Settings
    ConstGroup = OptionGroup(
        parser,
        title='Parameter Settings',
        description="Miscellaneous default values and settings")
    ConstGroup.add_option(
        "--Vp",
        action="store",
        type="float",
        dest="vp",
        default=6.,
        help="Specify default P velocity value. [Default 6.0 km/s]")
    ConstGroup.add_option(
        "--SNR",
        action="store",
        type="float",
        dest="msnr",
        default=7.5,
        help="Specify the SNR threshold used to determine whether " +
        "events are processedc. [Default 7.5]")
    ConstGroup.add_option(
        "--window",
        action="store",
        type="float",
        dest="dts",
        default=120.,
        help="Specify time window length before and after the " +
        "SKS arrival. The total window length is 2*dst. " +
        "[Default 120 s]")
    ConstGroup.add_option(
        "--max-delay",
        action="store",
        type="float",
        dest="maxdt",
        default=4.,
        help="Specify the maximum delay time. [Default 4 s]")
    ConstGroup.add_option(
        "--time-increment",
        action="store",
        type="float",
        dest="ddt",
        default=0.1,
        help="Specify the time increment. [Default 0.1 s]")
    ConstGroup.add_option(
        "--angle-increment",
        action="store",
        type="float",
        dest="dphi",
        default=1.,
        help="Specify the angle increment. [Default 1 d]")
    ConstGroup.add_option(
        "--transverse-SNR",
        action="store",
        type="float",
        dest="snrTlim",
        default=1.,
        help="Specify the minimum SNR Threshold for the Transverse " +
        "component to be considered Non-Null. [Default 1.]")

    # Event Selection Criteria
    EventGroup = OptionGroup(
        parser,
        title="Event Settings",
        description="Settings associated with " +
        "refining the events to include in matching station pairs")
    EventGroup.add_option(
        "--start-time",
        action="store",
        type="string",
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing the " +
        "start time for the event search. This will override any station " +
        "start times. [Default more recent start date for each station pair]")
    EventGroup.add_option(
        "--end-time",
        action="store",
        type="string",
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing the " +
        "end time for the event search. This will override any station " +
        "end times [Default older end date for each the pair of stations]")
    EventGroup.add_option(
        "--reverse-order", "-R",
        action="store_true",
        dest="reverse",
        default=False,
        help="Reverse order of events. Default behaviour starts at oldest " +
        "event and works towards most recent. Specify reverse order and " +
        "instead the program will start with the most recent events and " +
        "work towards older")
    EventGroup.add_option(
        "--min-mag",
        action="store",
        type="float",
        dest="minmag",
        default=6.0,
        help="Specify the minimum magnitude of event for which to search. " +
        "[Default 6.0]")
    EventGroup.add_option(
        "--max-mag",
        action="store",
        type="float",
        dest="maxmag",
        default=None,
        help="Specify the maximum magnitude of event for which to search. " +
        "[Default None, ie no limit]")

    # Geometry Settings
    GeomGroup = OptionGroup(
        parser,
        title="Geometry Settings",
        description="Settings associatd with "
        "the event-station geometries")
    GeomGroup.add_option(
        "--min-dist",
        action="store",
        type="float",
        dest="mindist",
        default=85.,
        help="Specify the minimum great circle distance (degrees) " +
        "between the station and event. [Default 85]")
    GeomGroup.add_option(
        "--max-dist",
        action="store",
        type="float",
        dest="maxdist",
        default=120.,
        help="Specify the maximum great circle distance (degrees) " +
        "between the station and event. [Default 120]")

    parser.add_option_group(EventGroup)
    parser.add_option_group(GeomGroup)
    parser.add_option_group(ConstGroup)
    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need Data Folder")
    indr = args[0]
    if not exist(indr):
        parser.error("Input Data Folder " + indr + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " + opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " + opts.endT)
    else:
        opts.endT = None

    return (opts, indr)

