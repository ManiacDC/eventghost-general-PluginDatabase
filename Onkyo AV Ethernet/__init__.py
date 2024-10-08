#
# Onkyo Ethernet
# ================

# Public Domain
#
#
# Revision history:
# -----------------
# 0.1 - initial
# 0.2 - revised by Bartman for Onkyo 805, switch to SerialThread
# 0.2 - revised by Fiasco for Onkyo 875
# 0.3 - revised by FoLLgoTT for Onkyo PR-SC5507 and converted to eISCP (ethernet)
# 0.4 - revised by ManiacDC to fix eISCP functionality and respond to events

help = """\
Plugin to control Onkyo A/V Receivers via Ethernet.
Developed for Onkyo A/V Receivers with ISCP interface. Note that 
not all commands work with every model."""

eg.RegisterPlugin(
    name = "Onkyo AV Ethernet",
    author = "prostetnic, Bartman, Fiasco, FoLLgoTT",
    version = "0.3." + "$LastChangedRevision: 1246 $".split()[1],
    kind = "external",
    guid = "{50e42894-579e-4ae2-9d9e-3b67c2c338ce}",
    description = "Control Onkyo A/V Receivers via Ethernet",
    help = help,
    canMultiLoad = True,
    createMacrosOnAdd = True,
    icon = (
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAA"
        "AAd0SU1FB9YDBAsPCqtpoiUAAAAWdEVYdFNvZnR3YXJlAFBhaW50Lk5FVCAyLjZsqHS1"
        "AAADe0lEQVQ4T02TXVCUZRSAPyZsxpnqoovum+miq+6qFUJYQP7cogS2VpGFAAlKpyAC"
        "EVh+4k80WGADQWlxZRfZACH5ECVY5TdHiEbAIQVkHRzUCZK/ZWGXp10SxjPzXrzvvM9z"
        "zpw5xwUQXg7ndX1jw3VkYmrzycK/gusrgrB3z17hvXfffv2tN99YcXHEi///g07Bznkw"
        "+9i1yvAbqvJKolRJhJ2KQp4ZQWTWd5wsV9Ni6sWybn3tZWYXvjt531V1tgJF8lcEZbij"
        "MLgRbTpAVHcgyk5/QnSefHrmc7QdV1hbX9+VbAvuTk67ZpfVIDsWgu/ZfURfD+TElVBy"
        "m4+TooshvDaAL697EPOHLzK1L9prbayuWbYlwsLzFZfCql+Qx8XhqfoAZUsIhsEGLGsW"
        "Nm12FlZtTM0/w2DSEmn0dEgclRSFcFG8wcamTRAqtO0kpRficdQLpV5Gr7mf3qFHzC1u"
        "YF61MvrIztD0OsP3F6m/ZUDZ7klosxfxJZn0j04hpJ+uIvZ4EpJvJKhvFWOzW1lc2qT/"
        "zznuzdnoGnlG+8BDWnvMDE7M8q1eQcygN6GFkWj0nQgp+WUcilTyUaIHzRPtWKx2rLYt"
        "5hfXHBnMNIjDtHbfY3RmmcdLdkrEfKIHDyDLPYS6vhnhh9wSgiPCcYvbT+3gNQbGluib"
        "WOTG8EOaTGOY/nrKwPgynXdm+H3gCZkNeQ6BP0GnZGgMRoTUnDMcSfgaiUJKWuPP6MRx"
        "LhjvUN3Qh671NnVNQ1y9Oe2YgUmaeqY4WnMEpSgl5ORhzhmaEFRFpSTnOpool+GXFoa6"
        "sQNNXReVupucv9zHeWM3Gl0HNY0mci7VEtF2EJ+8fSTkpSP23EaYmpl1ySgowk8ehiTc"
        "i6iiExRcNKC+0IlG20m5XqRCK5J9qYxoMZSgail+scEUn6vn+bJFImxtbQkl5dWoCkvx"
        "Cg3k/Uh3grKCSahJJln3E8n1BSQ2JhArHuSTUgneET6kFWno6h3GyW5P4sqqRUhMLSCn"
        "uJQA+cdIFYF8GC3F/Xs3vDM8kaZ4sP+YD/4RX5B+Wk1l3SXnkG2zu7uwZrHuqa1rILuw"
        "hNSsfOSxsQQoPkN2WI4iPp7EzBx+dPRLb7zK0orl1Z2FEmwvTM4HZ0kzZvM7hqZfMbaJ"
        "jEw8YHh8kvrGFmr1euaf/iPZAW12uzD2t1n4DwtSpLoLWTYZAAAAAElFTkSuQmCC"
    ),
)


import socket
import re
import binascii
import struct
import threading
import select


class ConnectionClosedException(Exception):
    """raised when connection is closed"""


cmdList = (
    ('Power / Sleep', None, None, None),
        ('PowerOff',               'Power Standby',                                              'PWR00',             None),
        ('PowerOn',                'Power On',                                                   'PWR01',             None),       
        ('PowerState',             'Returns Power State',                                        'PWRQSTN',           None),
        ('SleepTime',              'Sleep Time (01-5A, 1-90 in Hex, 1=---/MIN)',                 'SLP',               '0-90'),
        ('SleepOff',               'Sleep Off',                                                  'SLPOFF',            None),
        ('SleepToggle',            'Sleep Toggle',                                               'SLPUP',             None),
        ('SleepState',             'Returns Sleep State',                                        'SLPQSTN',           None),
    ('Master Volume', None, None, None),
        ('VolumeUp',               'Master Volume Up',                                           'MVLUP',             None),
        ('VolumeDown',             'Master Volume Down',                                         'MVLDOWN',           None),
        ('VolumeSet',              'Set Master Volume (0-64, 0-100 in Hex, 0=---/MIN)',          'MVL',               '0-64'),
        ('MuteOn',                 'Mute Off',                                                   'AMT00',             None),
        ('MuteOff',                'Mute On',                                                    'AMT01',             None),
        ('MuteToggle',             'Mute Toggle',                                                'AMTTG',             None),
    ('Speaker Level Calibration', None, None, None),
        ('LevelTest',              'Test',                                                       'SLCTEST',           None),
        ('LevelChannel',           'Channel',                                                    'SLCCHSEL',          None),
        ('LevelUp',                'Level Up',                                                   'SLCUP',             None),
        ('LevelDown',              'Level Down',                                                 'SLCDOWN',           None),
    ('Subwoofer Level Command Temporary', None, None, None),
        ('SubUp',                  'Level Up',                                                   'SWLUP',             None),
        ('SubDown',                'Level Down',                                                 'SWLDOWN',           None),
        ('SubState',               'Returns Subwoofer State',                                    'SWLQSTN',           None),
    ('Display Mode', None, None, None),
        ('DisplaySelector',        'Sets Selector and Volume Display Mode',                      'DIF00',             None),
        ('DisplayDigitalFormat',   'Display Digital Format',                                     'DIF02',             None),
        ('DisplayVideoFormat',     'Display Video Format',                                       'DIF03',             None),
        ('DisplayToggle',          'Display Mode Toggle',                                        'DIFTG',             None),
        ('DisplayState',           'Returns Display Mode',                                       'DIFQSTN',           None),
    ('Information', None, None, None),
        ('AudioInformation',       'Gets Information about Audio',                               'IFAQSTN',           None),
        ('VideoInformation',       'Gets Information about Video',                               'IFVQSTN',           None),
    ('Dimmer Level', None, None, None),
        ('DimBright',              'Bright',                                                     'DIM00',             None),
        ('DimDim',                 'Dim',                                                        'DIM01',             None),
        ('DimDark',                'Dark',                                                       'DIM02',             None),
        ('DimBrightLED',           'Bright with LED Off',                                        'DIM08',             None),
        ('DimToggle',              'Dimmer Toggle',                                              'DIMDIM',            None),
        ('DimState',               'Returns Dimmer Stage',                                       'DIMQSTN',           None),
    ('On Screen Display', None, None, None),
        ('OSDMenu',                'Menu',                                                       'OSDMENU',           None),
        ('OSDUp',                  'Up',                                                         'OSDUP',             None),
        ('OSDDown',                'Down',                                                       'OSDDOWN',           None),
        ('OSDRight',               'Right',                                                      'OSDRIGHT',          None),
        ('OSDLeft',                'Left',                                                       'OSDLEFT',           None),
        ('OSDEnter',               'Enter',                                                      'OSDENTER',          None),
        ('OSDExit',                'Exit',                                                       'OSDEXIT',           None),
    ('Memory Setup', None, None, None),
        ('MemStore',               'Store',                                                      'MEMSTR',            None),
        ('MemRecall',              'Recall',                                                     'MEMRCL',            None),
        ('MemLock',                'Lock',                                                       'MEMLOCK',           None),
        ('MemUnlock',              'Unlock',                                                     'MEMUNLK',           None),
    ('Input Select Command', None, None, None),
        ('InputVCR',               'VCR / DVR',                                                  'SLI00',             None),
        ('InputCBL',               'Cable / Satellite',                                          'SLI01',             None),
        ('InputGame',              'Game / TV',                                                  'SLI02',             None),
        ('InputAux1',              'Aux 1',                                                      'SLI03',             None),
        ('InputAux2',              'Aux 2',                                                      'SLI04',             None),
        ('InputPC',                'PC',                                                         'SLI05',             None),
        ('InputDVD',               'DVD',                                                        'SLI10',             None),
        ('InputTape',              'Tape',                                                       'SLI20',             None),
        ('InputPhono',             'Phono',                                                      'SLI22',             None),
        ('InputCD',                'CD',                                                         'SLI23',             None),
        ('InputFM',                'FM',                                                         'SLI24',             None),
        ('InputAM',                'AM',                                                         'SLI25',             None),
        ('InputTuner',             'Tuner',                                                      'SLI26',             None),
        ('MusicServer',            'Music Server',                                               'SLI27',             None),
        ('InternetRadio',          'Internet Radio',                                             'SLI28',             None),
        ('USBFront',               'USB (Front)',                                                'SLI29',             None),
        ('USBRear',                'USB (Rear)',                                                 'SLI2A',             None),
        ('InputXM',                'XM',                                                         'SLI31',             None),
        ('InputSirius',            'Sirius',                                                     'SLI32',             None),
        ('UniversalPort',          'Universal Port',                                             'SLI40',             None),
        ('InputUp',                'Next Input',                                                 'SLIUP',             None),
        ('InputDown',              'Previous Input',                                             'SLIDOWN',           None),
        ('InputState',             'Returns Current Input',                                      'SLIQSTN',           None),

    ('Audio Selector', None, None, None),
        ('AudioAuto',              'Auto',                                                       'SLA00',             None),
        ('AudioMulti',             'Multi-Channel',                                              'SLA01',             None),
        ('AudioAnalog',            'Analog',                                                     'SLA02',             None),
        ('AudioHDMI',              'HDMI',                                                       'SLA04',             None),
        ('AudioOptical',           'Coax / Optical',                                             'SLA05',             None),
        ('AudioBalance',           'Balance',                                                    'SLA06',             None),
        ('AudioUp',                'Toggle',                                                     'SLAUP',             None),
        ('AudioState',             'Returns Current Audio Selection',                            'SLAQSTN',           None),
    ('HDMI Output Selector', None, None, None),
        ('HDMIAnalog',             'Analog',                                                     'HDO00',             None),
        ('HDMIMain',               'Main',                                                       'HDO01',             None),
        ('HDMISub',                'Sub',                                                        'HDO02',             None),
        ('HDMIBoth',               'Both',                                                       'HDO03',             None),
        ('HDMIBothMain',           'Both (Main)',                                                'HDO04',             None),
        ('HDMIBothSub',            'Both (Sub)',                                                 'HDO05',             None),
        ('HDMIToggle',             'Toggle',                                                     'HDOUP',             None),
        ('HDMIState',              'Returns HDMI Output Selection',                              'HDQSTN',            None),
    ('Monitor Out Resolution', None, None, None),
        ('ResThrough',             'Through',                                                    'RES00',             None),
        ('ResAuto',                'Auto',                                                       'RES01',             None),
        ('Res480p',                '480p',                                                       'RES02',             None),
        ('Res720p',                '720p',                                                       'RES03',             None),
        ('Res1080i',               '1080i',                                                      'RES04',             None),
        ('Res1080p',               '1080p',                                                      'RES05',             None),
        ('Res1080p24fs',           '1080p 24fs',                                                 'RES07',             None),
        ('ResSource',              'Source',                                                     'RES06',             None),
        ('ResToggle',              'Toggle',                                                     'RESUP',             None),
        ('ResState',               'Get Current Resolution',                                     'RESQSTN',           None),
    ('ISF Mode', None, None, None),
        ('ISFModeCustom',          'Custom',                                                     'ISF00',             None),
        ('ISFModeDay',             'Day',                                                        'ISF01',             None),
        ('ISFModeNight',           'Night',                                                      'ISF02',             None),
        ('ISFModeToggle',          'Toggle',                                                     'ISFUP',             None),
        ('ISFModeState',           'Get Current ISF Mode',                                       'ISFQSTN',           None),
    ('Listening Mode', None, None, None),
        ('LMStereo',               'Stereo',                                                     'LMD00',             None),
        ('LMDirect',               'Direct',                                                     'LMD01',             None),
        ('LMSurround',             'Surround',                                                   'LMD02',             None),
        ('LMFilm',                 'Film/Game-RPG',                                              'LMD03',             None),
        ('LMTHX',                  'THX',                                                        'LMD04',             None),
        ('LMAction',               'Action/Game-Action',                                         'LMD05',             None),
        ('LMMusical',              'Musical/Game-Rock',                                          'LMD06',             None),
        ('LMMonoMovie',            'Mono Movie',                                                 'LMD07',             None),
        ('LMOrchestra',            'Orchestra',                                                  'LMD08',             None),
        ('LMUnplugged',            'Unplugged',                                                  'LMD09',             None),
        ('LMStudioMix',            'Studio Mix',                                                 'LMD0A',             None),
        ('LMTVLogic',              'TV Logic',                                                   'LMD0B',             None),
        ('LMAllChStero',           'All Channel Stereo',                                         'LMD0C',             None),
        ('LMTheatreDim',           'Theater Dimensional',                                        'LMD0D',             None),
        ('LMEnhanced',             'Enhanced/Game-Sports',                                       'LMD0E',             None),
        ('LMMono',                 'Mono',                                                       'LMD0F',             None),
        ('LMPureAudio',            'Pure Audio',                                                 'LMD11',             None),
        ('LMFullMono',             'Full Mono',                                                  'LMD13',             None),
        ('LMDTSSurSen',            'DTS Surround Sensation',                                     'LMD15',             None),
        ('LMAudysseyDSX',          'Audyssey DSX',                                               'LMD16',             None),
        ('LMStraightDecode',       'Straight Decode',                                            'LMD40',             None),
        ('LMDolbyEX',              'Dolby EX',                                                   'LMD41',             None),
        ('LMTHXCinema',            'THX Cinema',                                                 'LMD42',             None),
        ('LMTHXSurroundEX',        'THX Surround EX',                                            'LMD43',             None),
        ('LMTHXMusic',             'THX Music',                                                  'LMD44',             None),
        ('LMTHXGames',             'THX Games',                                                  'LMD45',             None),
        ('LMUSCinema',             'US/S2 Cinema',                                               'LMD50',             None),
        ('LMMusicMode',            'US/S2 Music Mode',                                           'LMD51',             None),
        ('LMGameMode',             'US/S2 Game Mode',                                            'LMD52',             None),
        ('LMPLIIMovie',            'PLII/PLIIx Movie',                                           'LMD80',             None),
        ('LMPLIIMusic',            'PLII/PLIIx Music',                                           'LMD81',             None),
        ('LMN6Cinema',             'Neo:6 Cinema',                                               'LMD82',             None),
        ('LMN6Music',              'Neo:6 Music',                                                'LMD83',             None),     
        ('LMPLIITHXCinema',        'PLII/PLIIx THX Cinema',                                      'LMD84',             None),
        ('LMN6THXCinema',          'Neo:6 THX Cinema',                                           'LMD85',             None),
        ('LMPLIIGame',             'PLII/PLIIx Game',                                            'LMD86',             None),
        ('LMNeuralTHX',            'Neural THX',                                                 'LMD88',             None),
        ('LMPLIITHXGame',          'PLII/PLIIx THX Game',                                        'LMD89',             None),
        ('LMN6THXGame',            'Neo:6 THX Game',                                             'LMD8A',             None),
        ('LMPLIITHXMusic',         'PLII/PLIIx THX Music',                                       'LMD8B',             None),
        ('LMN6THXMusic',           'Neo:6 THX Music',                                            'LMD8C',             None),
        ('LMNeuralTHXCinema',      'Neural THX Cinema',                                          'LMD8D',             None),
        ('LMNeuralTHXMusic',       'Neural THX Music',                                           'LMD8E',             None),
        ('LMNeuralTHXGames',       'Neural THX Games',                                           'LMD8F',             None),
        ('LMPLIIzHeight',          'PLIIz Height',                                               'LMD90',             None),
        ('LMN6CinemaDTSSurSen',    'Neo:6 Cinema DTS Surround Sensation',                        'LMD91',             None),
        ('LMN6MusicDTSSurSen',     'Neo:6 Music DTS Surround Sensation',                         'LMD92',             None),
        ('LMNeuralDigitalMusic',   'Neural Digital Music',                                       'LMD93',             None),
        ('LMPLIIzHTHXCinema',      'PLIIz Height THX Cinema',                                    'LMD94',             None),
        ('LMPLIIzHTHXMusic',       'PLIIz Height THX Music',                                     'LMD95',             None),
        ('LMPLIIzHTHXGames',       'PLIIz Height THX Games',                                     'LMD96',             None),
        ('LMPLIIzHTHXU2Cinema',    'PLIIz Height THX U2/S2 Cinema',                              'LMD97',             None),
        ('LMPLIIzHTHXU2Music',     'PLIIz Height THX U2/S2 Music',                               'LMD98',             None),
        ('LMPLIIzHTHXU2Games',     'PLIIz Height THX U2/S2 Games',                               'LMD99',             None),
        ('LMPLIIMovieDSX',         'PLII/PLIIx Movie + Audyssey DSX',                            'LMDA0',             None),
        ('LMPLIIMusicDSX',         'PLII/PLIIx Music + Audyssey DSX',                            'LMDA1',             None),
        ('LMPLIIGameDSX',          'PLII/PLIIx Game + Audyssey DSX',                             'LMDA2',             None),
        ('LMN6CinemaDSX',          'Neo:6 Cinema + Audyssey DSX',                                'LMDA3',             None),
        ('LMN6MusicDSX',           'Neo:6 Music + Audyssey DSX',                                 'LMDA4',             None),
        ('LMDolbyEXDSX',           'Dolby EX + Audyssey DSX',                                    'LMDA7',             None),
        ('LMUp',                   'Next Listening Mode',                                        'LMDUP',             None),
        ('LMDown',                 'Previous Listening Mode',                                    'LMDDOWN',           None),
        ('LMMovie',                'Next Movie Listening Mode',                                  'LMDMOVIE',          None),
        ('LMMusic',                'Next Music Listening Mode',                                  'LMDMUSIC',          None),
        ('LMGame',                 'Next Game Listening Mode',                                   'LMDGAME',           None),
        ('LMState',                'Returns Current Listening Mode',                             'LMDQSTN',           None),    
    ('Late Night', None, None, None),
        ('LNoff',                  'Late Night Off',                                             'LTN00',             None),
        ('LnLow',                  'Late Night Low',                                             'LTN01',             None),
        ('LNHigh',                 'Late Night High',                                            'LTN02',             None),
        ('LNAuto',                 'Late Night Auto',                                            'LTN03',             None),
        ('LNUp',                   'Late Night Toggle',                                          'LTNUP',             None),
        ('LNState',                'Returns Current Late Night State',                           'LTNQSTN',           None),
    ('Re-EQ', None, None, None),
        ('ReEQoff',                'Re-EQ Off',                                                  'RAS00',             None),
        ('ReEQOn',                 'Re-EQ On',                                                   'RAS01',             None),
        ('ReEqUp',                 'Re-EQ Toggle',                                               'RASUP',             None),
        ('ReEQState',              'Returns Current Re-EQ State',                                'RASQSTN',           None),
    ('Audyssey EQ', None, None, None),
        ('AudEQOff',               'Audyssey EQ Off',                                            'ADY00',             None),
        ('AudEQOn',                'Audyssey EQ On',                                             'ADY01',             None),
        ('AudEQToggle',            'Audyssey EQ Toggle',                                         'ADYUP',             None),
        ('AudEQState',             'Returns Current Audyssey EQ State',                          'ADYQSTN',           None),
    ('Audyssey Dynamic EQ', None, None, None),
        ('AudDynEQOff',            'Audyssey Dynamic EQ Off',                                    'ADQ00',             None),
        ('AudDynEQOn',             'Audyssey Dynamic EQ On',                                     'ADQ01',             None),
        ('AudDynEQToggle',         'Audyssey Dynamic EQ Toggle',                                 'ADQUP',             None),
        ('AudDynEQState',          'Returns Current Audyssey Dynamic EQ State',                  'ADQQSTN',           None),
    ('Audyssey Dynamic Volume', None, None, None),
        ('AudDynVOff',             'Audyssey Dynamic Volume Off',                                'ADV00',             None),
        ('AudDynVLight',           'Audyssey Dynamic Volume Light',                              'ADV01',             None),
        ('AudDynVMedium',          'Audyssey Dynamic Volume Medium',                             'ADV02',             None),
        ('AudDynVHeavy',           'Audyssey Dynamic Volume Heavy',                              'ADV03',             None),
        ('AudDynVToggle',          'Audyssey Dynamic Volume Toggle',                             'ADVUP',             None),
        ('AudDynVState',           'Returns Current Audyssey Dynamic Volume State',              'ADVQSTN',           None),        
    ('Dolby Volume', None, None, None),
        ('DolbyVolumeOff',         'Dolby Volume Off',                                           'DVL00',             None),
        ('DolbyVolumeLow',         'Dolby Volume Low',                                           'DVL01',             None),
        ('DolbyVolumeMid',         'Dolby Volume Mid',                                           'DVL02',             None),
        ('DolbyVolumeHigh',        'Dolby Volume High',                                          'DVL03',             None),
        ('DolbyVolumeToggle',      'Dolby Volume Toggle',                                        'DVLUP',             None),
        ('DolbyVolumeState',       'Returns Current Dolby Volume State',                         'DVLQSTN',           None),
    ('Music Optimizer', None, None, None),
        ('MusicOptimizerOff',      'Music Optimizer Off',                                        'MOT00',             None),
        ('MusicOptimizerOn',       'Music Optimizer On',                                         'MOT01',             None),
        ('MusicOptimizerToggle',   'Music Optimizer Toggle',                                     'MOTUP',             None),
        ('MusicOptimizerState',    'Returns Current Music Optimizer State',                      'MOTQSTN',           None),
    ('Radio Tuner', None, None, None),
        ('TuneFreq',               'Tune To Frequency nnnnn (0-64, 0-99999 in DEC, 0=---/MIN)',  'TUN',               '0-99999'),
        ('TuneUp',                 'Frequency Up',                                               'TUNUP',             None),
        ('TuneDown',               'Frequency Down',                                             'TUNDOWN',           None),
        ('TuneState',              'Retuns Current Frequency',                                   'TUNQSTN',           None),
    ('Preset Command', None, None, None),
        ('PresetSet',              'Set (1-28, 1-40 in HEX, 1=---/MIN)',                         'PRS',               '1-40'),
        ('PresetUp',               'Next',                                                       'PRSUP',             None),
        ('PresetDown',             'Previous',                                                   'PRSDOWN',           None),
        ('PresetState',            'Returns Current Preset',                                     'PRSQSTN',           None),       
    ('RDS Information (RDS Model Only)', None, None, None),
        ('RDSRT',                  'Display RT Information',                                     'RDS00',             None),
        ('RDSPTY',                 'DIsplay PTY Information',                                    'RDS01',             None),
        ('RDSTP',                  'Display TP Information',                                     'RDS02',             None),
        ('RDSTOGGLE',              'Toggle RDS Information',                                     'RDSUP',             None),  
    ('PTY Scan (RDS Model Only)', None, None, None),
        ('PTSScan',                'PTY (00-1E, 0-30 in HEX, 0=---/MIN)',                        'PTS',               '0-30'),
        ('PTSFinish',              'Finish PTY Scan',                                            'PTSENTER',          None),
    ('TP Scan (RDS Model Only)', None, None, None),
        ('TPScan',                 'Start Scan',                                                 'TPS',               None),
        ('TPFinish',               'Finish TP Scan',                                             'TPSENTER',          None),
    ('XM Info (XM Model Only)', None, None, None),
        ('XMChannel',              'Get XM Channel Name',                                        'XCNQSTN',           None),
        ('XMArtist',               'Get XM Artist Name',                                         'XATQSTN',           None),
        ('XMTitle',                'Get XM Title',                                               'XTIQSTN',           None),
        ('XMChannel',              'XM Channel (0-255 in DEC, 0=---/MIN)',                       'XCH',               '0-255'),
        ('XMUp',                   'Next Channel',                                               'XCHUP',             None),
        ('XMDown',                 'Previous Channel',                                           'XCHDOWN',           None),
        ('XMState',                'Get XM Channel Number',                                      'XCHQSTN',           None),
        ('XMCategoryUp',           'Next Category',                                              'XCTUP',             None),
        ('XMCategoryDown',         'Previous Category',                                          'XCTDOWN',           None),
        ('XMCategoryState',        'Get XM Category',                                            'XCTQSTN',           None),
    ('Sirius Info (Sirius Model Only)', None, None, None),
        ('SiriusChannel',          'Get Sirius Channel Name',                                    'SCNQSTN',           None),
        ('SiriusArtist',           'Get Sirius Artist Name',                                     'SATQSTN',           None),
        ('SiriusTitle',            'Get Sirius Title',                                           'STIQSTN',           None),
        ('SiriusChannel',          'Sirius Channel (0-255 in DEC, 0=---/MIN)',                   'SCH',               '0-255'),
        ('SiriusUp',               'Next Channel',                                               'SCHUP',             None),
        ('SiriusDown',             'Previous Channel',                                           'SCHDOWN',           None),
        ('SiriusState',            'Get Sirius Channel Number',                                  'SCHQSTN',           None),
        ('SiriusCategoryUp',       'Next Category',                                              'SCTUP',             None),
        ('SiriusCategoryDown',     'Previous Category',                                          'SCTDOWN',           None),
        ('SiriusCategoryState',    'Get Sirius Category',                                        'SCTQSTN',           None),
        ('SiriusLockCode',         'Lock Password (0-9999 in DEC, 0000=---/MIN)',                'SLK',               '0-9999'),
        ('SiriusInput',            'Input Lock Password',                                        'SLKINPUT',          None),
        ('SiriusWrong',            'Wrong Lock Password',                                        'SLKWRONG',          None),     
    ('Zone 2', None, None, None),
        ('Z2Standby',              'Power Off',                                                  'ZPW00',             None),
        ('Z2On',                   'Power On',                                                   'ZPW01',             None),
        ('Z2State',                'Returns Power State',                                        'ZPWQSTN',           None),
        ('Z2MuteOff',              'Muting Off',                                                 'ZMT00',             None),
        ('Z2MuteOn',               'Muting On',                                                  'ZMT01',             None),
        ('Z2MuteToggle',           'Muting Toggle',                                              'ZMTTG',             None),
        ('Z2MuteState',            'Returns Muting State',                                       'ZMTQSTN',           None),
        ('Z2VolumeSet',            'Set Volume Directly (0-64, 0-100 in Hex, 0=---/MIN)',        'ZVL',               '0-64'),
        ('Z2VolumeUp',             'Volume Up',                                                  'ZVLUP',             None),
        ('Z2VolumeDown',           'Volume Down',                                                'ZVLDOWN',           None),
        ('Z2VolumeState',          'Returns Volume State',                                       'ZVLQSTN',           None),
        ('Z2InputVCR',             'Input VCR',                                                  'SLZ00',             None),     
        ('Z2InputCBL/SAT',         'Input Cable / Satellite',                                    'SLZ01',             None),
        ('Z2InputGAME/TV',         'Input Game / TV',                                            'SLZ02',             None),
        ('Z2InputAUX1',            'Input Aux 1',                                                'SLZ03',             None),
        ('Z2InputAUX2',            'Input Aux 2',                                                'SLZ04',             None),
        ('Z2InputPC',              'Input PC',                                                   'SLZ05',             None),
        ('Z2InputDVD',             'Input DVD',                                                  'SLZ10',             None),
        ('Z2InputTAPE',            'Input Tape',                                                 'SLZ20',             None),
        ('Z2InputPHONO',           'Input Phono',                                                'SLZ22',             None),
        ('Z2InputCD',              'Input CD',                                                   'SLZ23',             None),
        ('Z2InputFM',              'Input FM',                                                   'SLZ24',             None),
        ('Z2InputAM',              'Input AM',                                                   'SLZ25',             None),
        ('Z2InputTUNER',           'Input Tuner',                                                'SLZ26',             None),
        ('Z2InputXM',              'Input XM',                                                   'SLZ31',             None),
        ('Z2InputSIRIUS',          'Input Sirius',                                               'SLZ32',             None),
        ('Z2InputOFF',             'Input Off',                                                  'SLZ7F',             None),
        ('Z2InputSOURCE',          'Input Source',                                               'SLZ80',             None),
        ('Z2InputState',           'Returns Input State',                                        'SLZQSTN',           None),
        ('Z2TunerFrequency',       'Tuner Frequency nnnnn (0-99999 in Dec, 0=---/MIN)',          'TUZ',               '0-99999'),
        ('Z2TunerUp',              'Tuner Frequency Up',                                         'TUZUP',             None),
        ('Z2TunerDown',            'Tuner Frequency Down',                                       'TUZDOWN',           None),
        ('Z2TunerState',           'Returns Tuner State',                                        'TUZQSTN',           None),
        ('Z2Preset',               'Set Preset (1-40, 1-28 in Hex, 1=---/MIN)',                  'PRZ',               '1-40'),
        ('Z2PresetUp',             'Preset Up',                                                  'PRZUP',             None),
        ('Z2PresetDown',           'Preset Down',                                                'PRZDOWN',           None),
        ('Z2PresetState',          'Returns Preset State',                                       'PRZQSTN',           None),
    ('Zone 3', None, None, None),
        ('Z3Standby',              'Power Off',                                                  'PW300',             None),
        ('Z3On',                   'Power On',                                                   'PW301',             None),
        ('Z3State',                'Returns Power State',                                        'PW3QSTN',           None),
        ('Z3MuteOff',              'Muting Off',                                                 'MT300',             None),
        ('Z3MuteOn',               'Muting On',                                                  'MT301',             None),
        ('Z3MuteToggle',           'Muting Toggle',                                              'MT3TG',             None),
        ('Z3MuteState',            'Returns Muting State',                                       'MT3QSTN',           None),
        ('Z3VolumeSet',            'Set Volume Directly (0-64, 0-100 in Hex, 0=---/MIN)',        'VL3',               '0-64'),
        ('Z3VolumeUp',             'Volume Up',                                                  'VL3UP',             None),
        ('Z3VolumeDown',           'Volume Down',                                                'VL3DOWN',           None),
        ('Z3VolumeState',          'Returns Volume State',                                       'VL3QSTN',           None),
        ('Z3InputVCR',             'Input VCR',                                                  'SL300',             None),     
        ('Z3InputCBL/SAT',         'Input Cable / Satellite',                                    'SL301',             None),
        ('Z3InputGAME/TV',         'Input Game / TV',                                            'SL302',             None),
        ('Z3InputAUX1',            'Input Aux 1',                                                'SL303',             None),
        ('Z3InputAUX2',            'Input Aux 2',                                                'SL304',             None),
        ('Z3InputPC',              'Input PC',                                                   'SL305',             None),
        ('Z3InputDVD',             'Input DVD',                                                  'SL310',             None),
        ('Z3InputTAPE',            'Input Tape',                                                 'SL320',             None),
        ('Z3InputPHONO',           'Input Phono',                                                'SL322',             None),
        ('Z3InputCD',              'Input CD',                                                   'SL323',             None),
        ('Z3InputFM',              'Input FM',                                                   'SL324',             None),
        ('Z3InputAM',              'Input AM',                                                   'SL325',             None),
        ('Z3InputTUNER',           'Input Tuner',                                                'SL326',             None),
        ('Z3InputXM',              'Input XM',                                                   'SL331',             None),
        ('Z3InputSIRIUS',          'Input Sirius',                                               'SL332',             None),
        ('Z3InputOFF',             'Input Off',                                                  'SL37F',             None),
        ('Z3InputSOURCE',          'Input Source',                                               'SL380',             None),
        ('Z3InputState',           'Returns Input State',                                        'SL3QSTN',           None),
        ('Z3TunerFrequency',       'Tuner Frequency nnnnn (0-99999 in Dec, 0=---/MIN)',          'TU3',               '0-99999'),
        ('Z3TunerUp',              'Tuner Frequency Up',                                         'TU3UP',             None),
        ('Z3TunerDown',            'Tuner Frequency Down',                                       'TU3DOWN',           None),
        ('Z3TunerState',           'Returns Tuner State',                                        'TU3QSTN',           None),
        ('Z3Preset',               'Set Preset (1-40, 1-28 in Hex, 1=---/MIN)',                  'PR3',               '1-40'),
        ('Z3PresetUp',             'Preset Up',                                                  'PR3UP',             None),
        ('Z3PresetDown',           'Preset None',                                                'PR3DOWN',           None),
        ('Z3PresetState',          'Returns Preset State',                                       'PR3QSTN',           None),
    ('R1 Commands CD', None, None, None),
        ('R1CDPower',              'Power On/Off',                                               'CCDPOWER',          None),
        ('R1CDTrack',              'Track',                                                      'CCDTRACK',          None),
        ('R1CDPlay',               'Play',                                                       'CCDPLAY',           None),
        ('R1CDStop',               'Stop',                                                       'CCDSTOP',           None),
        ('R1CDPause',              'Pause',                                                      'CCDPAUSE',          None),
        ('R1CDNext',               'Next',                                                       'CCDSKIP.F',         None),
        ('R1CDPrev',               'Previous',                                                   'CCDSKIP.R',         None),
        ('R1CDMemory',             'Memory',                                                     'CCDMEMORY',         None),
        ('R1CDClear',              'Clear',                                                      'CCDCLEAR',          None),
        ('R1CDRepeat',             'Repeat',                                                     'CCDREPEAT',         None),
        ('R1CDRandom',             'Random',                                                     'CCDRANDOM',         None),
        ('R1CDDisp',               'Display',                                                    'CCDDISP',           None),
        ('R1CDDMode',              'D.Mode',                                                     'CCDD.MODE',         None),
        ('R1CDFF',                 'Fast Foward',                                                'CCDFF',             None),
        ('R1CDRew',                'Rewind',                                                     'CCDREW',            None),
        ('R1CDOpen',               'Open/Close Tray',                                            'CCDOP/CL',          None),
        ('R1CD1',                  '1',                                                          'CCD1',              None),
        ('R1CD2',                  '2',                                                          'CCD2',              None),
        ('R1CD3',                  '3',                                                          'CCD3',              None),
        ('R1CD4',                  '4',                                                          'CCD4',              None),
        ('R1CD5',                  '5',                                                          'CCD5',              None),
        ('R1CD6',                  '6',                                                          'CCD6',              None),
        ('R1CD7',                  '7',                                                          'CCD7',              None),
        ('R1CD8',                  '8',                                                          'CCD8',              None),
        ('R1CD9',                  '9',                                                          'CCD9',              None),
        ('R1CD0',                  '0',                                                          'CCD0',              None),
        ('R1CD10Plus',             '10+',                                                        'CCD10+',            None),
        ('R1CDDISCF',              'Disc Forward',                                               'CCDDISC.F',         None),
        ('R1CDDISCR',              'Disc Back',                                                  'CCDDISC.R',         None),
        ('R1CDDISC1',              'Disc 1',                                                     'CCDDISC1',          None),
        ('R1CDDISC2',              'Disc 2',                                                     'CCDDISC2',          None),
        ('R1CDDISC3',              'Disc 3',                                                     'CCDDISC3',          None),
        ('R1CDDISC4',              'Disc 4',                                                     'CCDDISC4',          None),
        ('R1CDDISC5',              'Disc 5',                                                     'CCDDISC5',          None),
        ('R1CDDISC6',              'Disc 6',                                                     'CCDDISC6',          None),
        ('R1CDStandby',            'Standby',                                                    'CCDSTBY',           None),
        ('R1CDPowerOn',            'Power On',                                                   'CCDPON',            None),
    ('R1 Commands Tape A', None, None, None),
        ('R1Tape1PlayF',            'Play Forward',                                              'CT1PLAY.F',         None),
        ('R1Tape1PlayR',            'Play Rewind',                                               'CT1PLAY.R',         None),
        ('R1Tape1Stop',             'Stop',                                                      'CT1STOP',           None),
        ('R1Tape1Record',           'Record / Pause',                                            'CT1RC/PAU',         None),
        ('R1Tape1FF',               'Fast Forward',                                              'CT1FF',             None),
        ('R1Tape1Rew',              'Rewind',                                                    'CT1REW',            None),
    ('R1 Commands Tape B', None, None, None),
        ('R1Tape2PlayF',            'Play Forward',                                              'CT2PLAY.F',         None),
        ('R1Tape2PlayR',            'Play Rewind',                                               'CT2PLAY.R',         None),
        ('R1Tape2Stop',             'Stop',                                                      'CT2STOP',           None),
        ('R1Tape2Pause',            'Record / Pause',                                            'CT2RC/PAU',         None),
        ('R1Tape2FF',               'Fast Forward',                                              'CT2FF',             None),
        ('R1Tape2Rew',              'Rewind',                                                    'CT2REW',            None),
        ('R1Tape2Open',             'Open / Close',                                              'CT2OP/CL',          None),
        ('R1Tape2Skip',             'Skip Forward',                                              'CT2SKIP.F',         None),
        ('R1Tape2Prev',             'Skip Backward',                                             'CT2SKIP.R',         None),
        ('R1Tape2Record',           'Record',                                                    'CT2REC',            None),
    ('R1 Commands DVD', None, None, None),
        ('R1DVDPower',              'Power On/Off',                                              'CDVPOWER',          None),
        ('R1DVDPowerOn',            'Power On',                                                  'CDVPON',            None),
        ('R1DVDPowerOff',           'Power Off',                                                 'CDVPOFF',           None),
        ('R1DVDPlay',               'Play',                                                      'CDVPLAY',           None),
        ('R1DVDStop',               'Stop',                                                      'CDVSTOP',           None),
        ('R1DVDNext',               'Next',                                                      'CDVSKIP.F',         None),
        ('R1DVDPrev',               'Previous',                                                  'CDVSKIP.R',         None),
        ('R1DVDFF',                 'Fast Foward',                                               'CDVFF',             None),
        ('R1DVDRew',                'Rewind',                                                    'CDVREW',            None),
        ('R1DVDPause',              'Pause',                                                     'CDVPAUSE',          None),
        ('R1DVDLastPlay',           'Last Play',                                                 'CDVLASTPLAY',       None),
        ('R1DVDSubtitleToggle',     'Subtitle Toggle',                                           'CDVSUBTON/OFF',     None),
        ('R1DVDSubtitle',           'Subtitle',                                                  'CDVSUBTITLE',       None),
        ('R1DVDSetup',              'Setup',                                                     'CDVSETUP',          None),
        ('R1DVDTopMenu',            'Top Menu',                                                  'CDVTOPMENU',        None),
        ('R1DVDMenu',               'Menu',                                                      'CDVMENU',           None),
        ('R1DVDUp',                 'Up',                                                        'CDVUP',             None),
        ('R1DVDDown',               'Down',                                                      'CDVDOWN',           None),
        ('R1DVDLeft',               'Left',                                                      'CDVLEFT',           None),
        ('R1DVDRight',              'Right',                                                     'CDVRIGHT',          None),
        ('R1DVDEnter',              'Enter',                                                     'CDVENTER',          None),
        ('R1DVDReturn',             'Return',                                                    'CDVRETURN',         None),
        ('R1DVDDISCF',              'Disc Forward',                                              'CDVDISC.F',         None),
        ('R1DVDDISCR',              'Disc Back',                                                 'CDVDISC.R',         None),
        ('R1DVDAudio',              'Audio',                                                     'CDVAUDIO',          None),
        ('R1DVDRandom',             'Random',                                                    'CDVRANDOM',         None),
        ('R1DVDOpen',               'Open/Close Tray',                                           'CDVOP/CL',          None),
        ('R1DVDAngle',              'Angle',                                                     'CDVANGLE',          None),
        ('R1DVD1',                  '1',                                                         'CDV1',              None),
        ('R1DVD2',                  '2',                                                         'CDV2',              None),
        ('R1DVD3',                  '3',                                                         'CDV3',              None),
        ('R1DVD4',                  '4',                                                         'CDV4',              None),
        ('R1DVD5',                  '5',                                                         'CDV5',              None),
        ('R1DVD6',                  '6',                                                         'CDV6',              None),
        ('R1DVD7',                  '7',                                                         'CDV7',              None),
        ('R1DVD8',                  '8',                                                         'CDV8',              None),
        ('R1DVD9',                  '9',                                                         'CDV9',              None),
        ('R1DVD0',                  '0',                                                         'CDV0',              None),
        ('R1DVD10',                 '10',                                                        'CDV10',             None),
        ('R1DVDSearch',             'Search',                                                    'CDVSEARCH',         None),
        ('R1DVDDisplay',            'Display',                                                   'CDvDISP',           None),
        ('R1DVDRepeat',             'Repeat',                                                    'CDvREPEAT',         None),
        ('R1DVDMemory',             'Memory',                                                    'CDvMEMORY',         None),
        ('R1DVDClear',              'Clear',                                                     'CDvCLEAR',          None),
        ('R1DVDABRepeat',           'A-B Repeat',                                                'CDVABR',            None),
        ('R1DVDStep',               'Step',                                                      'CDVSTEP.F',         None),
        ('R1DVDStepBack',           'Step Back',                                                 'CDVSTEP.R',         None),
        ('R1DVDSlow',               'Slow',                                                      'CDVSLOW.F',         None),
        ('R1DVDSlowBack',           'Slow Back',                                                 'CDVSLOW.R',         None),        
        ('R1DVDZoom',               'Zoom',                                                      'CDVZOOMTG',         None),
        ('R1DVDZoomUp',             'Zoom Up',                                                   'CDVZOOMUP',         None),
        ('R1DVDZoomDown',           'Zoom Down',                                                 'CDVZOOMDOWN',       None),
        ('R1DVDProgressive',        'Progressive',                                               'CDVPROGRE',         None),
        ('R1DVDVideoToggle',        'Video On/Off',                                              'CDVVDOFF',          None),
        ('R1DVDCondition',          'Condition Memory',                                          'CDVCONMEN',         None),
        ('R1DVDFunction',           'Function Memory',                                           'CDVFUNMEN',         None),
        ('R1DVDDISC1',              'Disc 1',                                                    'CDVDISC1',          None),
        ('R1DVDDISC2',              'Disc 2',                                                    'CDVDISC2',          None),
        ('R1DVDDISC3',              'Disc 3',                                                    'CDVDISC3',          None),
        ('R1DVDDISC4',              'Disc 4',                                                    'CDVDISC4',          None),
        ('R1DVDDISC5',              'Disc 5',                                                    'CDVDISC5',          None),
        ('R1DVDDISC6',              'Disc 6',                                                    'CDVDISC6',          None),
        ('R1DVDFolderUp',           'Folder Up',                                                 'CDVFOLDUP',         None),
        ('R1DVDFolderDown',         'Folder Down',                                               'CDVFOLDDOWN',       None),
        ('R1DVDPlayMode',           'Play Mode',                                                 'CDVP.MODE',         None),
        ('R1DVDAspect',             'Aspect Toggle',                                             'CDVASCTG',          None),
        ('R1DVDCDRepeat',           'CD Chain Repeat',                                           'CDVCDPCD',          None),
        ('R1DVDMultiUp',            'Multi Speed Up',                                            'CDVMSPUP',          None),
        ('R1DVDMultiDown',          'Multi Speed Down',                                          'CDVMSPDN',          None),
        ('R1DVDPicture',            'Picture Control',                                           'CDVPCT',            None),
        ('R1DVDResolution',         'Resolution Toggle',                                         'CDVRSCTG',          None),
    ('R1 Commands MD Recorder', None, None, None),                
        ('R1MDPower',              'Power On/Off',                                               'CMDPOWER',          None),
        ('R1MDPlay',               'Play',                                                       'CMDPLAY',           None),
        ('R1MDStop',               'Stop',                                                       'CMDSTOP',           None),
        ('R1MDFF',                 'Fast Foward',                                                'CMDFF',             None),
        ('R1MDRew',                'Rewind',                                                     'CMDREW',            None),
        ('R1MDPMode',              'Play Mode',                                                  'CMDP.MODE',         None),
        ('R1MDSkip',               'Skip Forward',                                               'CMDSKIP.F',         None),
        ('R1MDPrev',               'Skip Backward',                                              'CMDSKIP.R',         None),
        ('R1MDPause',              'Pause',                                                      'CMDPAUSE',          None),
        ('R1MDRecord',             'Record',                                                     'CMDREC',            None),
        ('R1MDMemory',             'Memory',                                                     'CMDMEMORY',         None),
        ('R1MDDisp',               'Display',                                                    'CMDDISP',           None),
        ('R1MDScroll',             'Scroll',                                                     'CMDSCROLL',         None),
        ('R1MDScan',               'Music Scan',                                                 'CMDM.SCAN',         None),
        ('R1MDClear',              'Clear',                                                      'CMDCLEAR',          None),
        ('R1MDRandom',             'Random',                                                     'CMDRANDOM',         None),
        ('R1MDRepeat',             'Repeat',                                                     'CMDREPEAT',         None),
        ('R1MDEnter',              'Enter',                                                      'CMDENTER',          None),
        ('R1MDEject',              'Eject',                                                      'CMDEJECT',          None),
        ('R1MD1',                  '1',                                                          'CMD1',              None),
        ('R1MD2',                  '2',                                                          'CMD2',              None),
        ('R1MD3',                  '3',                                                          'CMD3',              None),
        ('R1MD4',                  '4',                                                          'CMD4',              None),
        ('R1MD5',                  '5',                                                          'CMD5',              None),
        ('R1MD6',                  '6',                                                          'CMD6',              None),
        ('R1MD7',                  '7',                                                          'CMD7',              None),
        ('R1MD8',                  '8',                                                          'CMD8',              None),
        ('R1MD9',                  '9',                                                          'CMD9',              None),
        ('R1MD0',                  '10/0',                                                       'CMD10/0',           None),       
        ('R1MDName',               'Name',                                                       'CMDNAME',           None),
        ('R1MDGroup',              'Group',                                                      'CMDGROUP',          None),
        ('R1MDStandby',            'Standby',                                                    'CMDSTBY',           None),
    ('R1 Commands CD-R Recorder', None, None, None),                
        ('R1CDRPower',              'Power On/Off',                                              'CCRPOWER',          None),
        ('R1CDRPlayMode',           'Play Mode',                                                 'CCRP.MODE',         None),
        ('R1CDRPlay',               'Play',                                                      'CCRPLAY',           None),
        ('R1CDRStop',               'Stop',                                                      'CCRSTOP',           None),
        ('R1CDRSkip',               'Skip Forward',                                              'CCRSKIP.F',         None),
        ('R1CDRPrev',               'Skip Backward',                                             'CCRSKIP.R',         None),
        ('R1CDRPause',              'Pause',                                                     'CCRPAUSE',          None),
        ('R1CDRClear',              'Clear',                                                     'CCRCLEAR',          None),
        ('R1CDRRepeat',             'Repeat',                                                    'CCRREPEAT',         None),
        ('R1CDR1',                  '1',                                                         'CCR1',              None),
        ('R1CDR2',                  '2',                                                         'CCR2',              None),
        ('R1CDR3',                  '3',                                                         'CCR3',              None),
        ('R1CDR4',                  '4',                                                         'CCR4',              None),
        ('R1CDR5',                  '5',                                                         'CCR5',              None),
        ('R1CDR6',                  '6',                                                         'CCR6',              None),
        ('R1CDR7',                  '7',                                                         'CCR7',              None),
        ('R1CDR8',                  '8',                                                         'CCR8',              None),
        ('R1CDR9',                  '9',                                                         'CCR9',              None),
        ('R1CDR0',                  '10/0',                                                      'CCR10/0',            None),       
        ('R1CDRSroll',              'Scroll',                                                    'CCRSCROLL',         None),
        ('R1CDROpen',               'Open/Close',                                                'CCROP/CL',          None),
        ('R1CDRDisplay',            'Display',                                                   'CCRDISP',           None),      
        ('R1CDRRandom',             'Random',                                                    'CCRRANDOM',         None),
        ('R1CDRMemory',             'Memory',                                                    'CCRMEMORY',         None),
        ('R1CDRFF',                 'Fast Forward',                                              'CCRFF',             None),
        ('R1CDRRew',                'Rewind',                                                    'CCRREW',            None),
        ('R1CDRStandby',            'Standby',                                                   'CCRSTBY',           None),       
    (None, None, None, None),       
         

)

def send_cmd(plugin, cmd):
    data = struct.pack(">4sIIcxxx%ssc" % len(cmd), b"ISCP", 16, len(cmd) + 1, b"\x01", cmd, b"\r")
    try:
        plugin.sock.sendall(data)
    except socket.error:
        plugin.connect()
        plugin.sock.sendall(data)




def extract_eiscp_header(header):
    """extracts header data from an eiscp packet"""

    if not header.startswith(b"ISCP"):
        return
    header_size = int(header[4:8].encode('hex'), 16)
    data_size = int(header[8:12].encode('hex'), 16)

    return header_size, data_size


class CmdAction(eg.ActionClass):
    """Base class for all argumentless actions"""

    def __call__(self):
        send_cmd(self.plugin, self.cmd)



class ValueAction(eg.ActionWithStringParameter):
    """Base class for all actions with adjustable argument"""

    def __call__(self, data):
        send_cmd(self.plugin, self.cmd + data)


class Raw(eg.ActionWithStringParameter):
    name = 'Send Raw command'

    def __call__(self, data):
        send_cmd(self.plugin, b'!1' + data)

class OnkyoEthernet(eg.PluginClass):

    def __init__(self):
        group = self

        for cmd_name, cmd_text, cmd_cmd, cmd_rangespec in cmdList:
            if cmd_text is None:
                # New subgroup, or back up
                if cmd_name is None:
                    group = self
                else:
                    group = self.AddGroup(cmd_name)
            elif cmd_rangespec is not None:
                # Command with argument
                actionName, paramDescr = cmd_text.split("(")
                actionName = actionName.strip()
                paramDescr = paramDescr[:-1]
                minValue, maxValue = cmd_rangespec.split("-")

                class Action(ValueAction):
                    name = actionName
                    cmd = "!1" + cmd_cmd
                    parameterDescription = "Value: (%s)" % paramDescr
                Action.__name__ = cmd_name
                group.AddAction(Action)
            else:
                # Argumentless command
                class Action(CmdAction):
                    name = cmd_text
                    cmd ="!1" + cmd_cmd
                Action.__name__ = cmd_name
                group.AddAction(Action)

        group.AddAction(Raw)

        onOffDict = {
            '00': 'Off',
            '01': 'On',
        }

        inputDict = {
            '00': 'Video1',
            '01': 'Video2',
            '02': 'Video3',
            '03': 'Video4',
            '04': 'Video5',
            '05': 'PC',
            '10': 'DVD',
            '20': 'Tape1',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '27': 'MusicServer',
            '28': 'InternetRadio',
            '29': 'USBFront',
            '2A': 'USBRear',
            '40': 'UniversalPort',
            '30': 'MultiChannel',
            '32': 'Sirius'
        }

        listeningModes = {
            '00': 'Stereo',
            '01': 'Direct',
            '02': 'Surround',
            '03': 'Film',
            '04': 'THX',
            '05': 'Action',
            '06': 'Musical',
            '07': 'MonoMovie',
            '08': 'Orchestra',
            '09': 'Unplugged',
            '0A': 'StudioMix',
            '0B': 'TvLogic',
            '0C': 'AllChStereo',
            '0D': 'TheatreDim',
            '0E': 'Enhanced',
            '0F': 'Mono',
            '11': 'PureAudio',
            '13': 'FullMono',
            '15': 'DTSSurSen',
            '16': 'AudysseyDSX',
            '40': 'Surround51ch',
            '41': 'DolbyEX',
            '42': 'THXCinema',
            '43': 'THXSurroundEX',
            '44': 'THXMusic',
            '45': 'THXGames',
            '50': 'Cinema2',
            '51': 'MusicMode',
            '52': 'GamesMode',
            '80': 'PLIIMovie',
            '81': 'PLIIMusic',
            '82': 'Neo6Cinema',
            '83': 'Neo6Music',
            '84': 'PLIITHXCinema',
            '85': 'Neo6THXCinema',
            '86': 'PLIIGame',
            '88': 'NeuralTHX',
            '89': 'PLIITHXGame',
            '8A': 'Neo6THXGame',
            '8B': 'PLIITHXMusic',
            '8C': 'Neo6THXMusic',
            '8D': 'NeuralTHXCinema',
            '8E': 'NeuralTHXMusic',
            '8F': 'NeuralTHXGames',
            '90': 'PLIIzHeight',
            '91': 'Neo6CinemaDTSSurSen',
            '92': 'Neo6MusicDTSSurSen',
            '93': 'NeuralDigitalMusic',
            '94': 'PLIIzHTHXCinema',
            '95': 'PLIIzHTHXMusic',
            '96': 'PLIIzHTHXGames',
            '97': 'PLIIzHTHXU2Cinema',
            '98': 'PLIIzHTHXU2Music',
            '99': 'PLIIzHTHXU2Games',
            'A0': 'PLIIMovieDSX',
            'A1': 'PLIIMusicDSX',
            'A2': 'PLIIGameDSX',
            'A3': 'Neo6CinemaDSX',
            'A4': 'Neo6MusicDSX',
            'A7': 'DolbyEXDSX'
        }
        
        self.commandDict = {
            'PWR': ('Power', onOffDict),
            'AMT': ('Muting', onOffDict),
            'LMD': ('ListeningModes', listeningModes),
            'SLI': ('Input', inputDict)
        }

    def __start__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.connect()
        self.listener_thread = threading.Thread(target=self.listen_forever)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))



    def __stop__(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        return

    def Configure(self, host="127.0.0.1", port=60128):
        panel = eg.ConfigPanel()
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, max=65535)

        panel.AddLine("Host:", hostCtrl)
        panel.AddLine("Port:", portCtrl)

        while panel.Affirmed():
            panel.SetResult(
                hostCtrl.GetValue(),
                portCtrl.GetValue()
            )

    def check_for_message(self):
        return select.select([self.sock], [], [], 0.1)[0]

    def listen_forever(self):
        while True:
            ready = self.check_for_message()
            if ready:
                message = self.get_message()
                if message:
                    self.process_message(message)

    def get_message(self):
        """receives data on a TCP socket and ensures it's terminated"""
        header = b""
        while self.check_for_message():
            data = self._tcp_grab_bytes(1)
            if data == b"I":
                header += data
                break
            if not data:
                raise ConnectionClosedException()

        header += self._tcp_grab_bytes(15)

        header_data = extract_eiscp_header(header)

        if not header_data:
            return

        if header_data[0] > 16:
            # grab remaining header data
            self._tcp_grab_bytes(header_data[0] - 16)

        message = self._tcp_grab_bytes(header_data[1])

        if not message:
            return

        while message.endswith(b"\r") or message.endswith(b"\n") or message.endswith(b"\x1A"):
            message = message[:-1]

        if not message.startswith(b"!1"):
            return

        return message

    def _tcp_grab_bytes(self, num_bytes):
        """grabs num_bytes bytes from tcp buffer"""
        data = b""
        for _ in range(num_bytes):
            ready = select.select([self.sock], [], [], 1)[0]
            if ready:
                try:
                    data += self.sock.recv(1)
                except socket.error:
                    self.connect()
                    data += self.sock.recv(1)
            else:
                # timeout hit, did not receive expected bytes
                return None
        return data
    
    def process_message(self, buffer):
        if not buffer.startswith("!1"):
            return
        command = buffer[2:5]
        value =  buffer[5:]

        #Generic
        if self.commandDict.has_key(command):
            eventNameDict = self.commandDict[command][1]
            if eventNameDict.has_key(value):
                value = eventNameDict[value]
            self.TriggerEvent(self.commandDict[command][0] + '.' + value)
            return

        #MasterVolume
        if command == "MVL":
            self.TriggerEvent("MasterVolume", int(value, 16))
            return

        #Sleep Timer
        if command == "SLP":
            payload = -1
            if value == "OFF":
                payload = 0
            if len(value) == 2:
                payload = int(value, 16)
            self.TriggerEvent("SleepTimer", payload)
            return

        self.TriggerEvent(command + "." + value,)
        return
