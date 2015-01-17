from esc import ESC, ST, NUL
from esclog import LogDebug, LogInfo, LogError, Print
import esctypes
import os
import sys
import tty

stdin_fd = None
stdout_fd = None
gSideChannel = None

def Init():
  global stdout_fd
  global stdin_fd

  stdout_fd = os.fdopen(sys.stdout.fileno(), 'w', 0)
  stdin_fd = os.fdopen(sys.stdin.fileno(), 'r', 0)
  tty.setraw(stdin_fd)

def Shutdown():
  tty.setcbreak(stdin_fd)

def Write(s, sideChannelOk=True):
  global gSideChannel
  if sideChannelOk and gSideChannel is not None:
    gSideChannel.write(s)
  stdout_fd.write(s)

def SetSideChannel(filename):
  global gSideChannel
  if filename is None:
    if gSideChannel:
      gSideChannel.close()
      gSideChannel = None
  else:
    gSideChannel = open(filename, "w")

def WriteCSI(prefix="", params=[], intermediate="", final="", requestsReport=False):
  str_params = map(str, params)
  joined_params = ";".join(str_params)
  sequence = ESC + "[" + prefix + joined_params + intermediate + final
  LogDebug("Send sequence: " + sequence.replace(ESC, "<ESC>"))
  Write(sequence, sideChannelOk=not requestsReport)

def ReadOrDie(e):
  c = read(1)
  AssertCharsEqual(c, e)

def AssertCharsEqual(c, e):
  if c != e:
    raise esctypes.InternalError("Read %c (0x%02x), expected %c (0x%02x)" % (c, ord(c), e, ord(e)))

def ReadCSI(expected_final, expected_prefix=None):
  """ Read a CSI code ending with |expected_final| and returns an array of parameters. """

  ReadOrDie(ESC)
  ReadOrDie('[')

  params = []
  current_param = ""

  c = read(1)
  if not c.isdigit() and c != ';':
    if c == expected_prefix:
      c = read(1)
    else:
      raise esctypes.InternalError("Unexpected character 0x%02x" % ord(c))

  while True:
    if c == ";":
      params.append(int(current_param))
      current_param = ""
    elif c >= '0' and c <= '9':
      current_param += c
    else:
      AssertCharsEqual(c, expected_final)
      if current_param == "":
        params.append(None)
      else:
        params.append(int(current_param))
      break
    c = read(1)
  return params

def ReadDCS():
  """ Read a DCS code. Returns the characters between DCS and ST. """
  assert read(1) == ESC
  assert read(1) == 'P'

  result = ""
  while not result.endswith(ST):
    result += read(1)
  return result[:-2]

def read(n):
  s = ""
  for i in xrange(n):
    s += stdin_fd.read(1)
  return s


