import esccsi
import escio
from escutil import AssertEQ, knownBug

class DATests(object):
  def __init__(self, args):
    self._args = args

  @knownBug(terminal="xterm", reason="xterm double-reports 6.")
  @knownBug(terminal="iTerm2", reason="iTerm2 doesn't report 18 or 22.")
  def handleDAResponse(self):
    params = escio.ReadCSI('c', expected_prefix='?')
    if self._args.expected_terminal == "xterm":
      # This is for a default build. There are various options that could
      # change this (disabling ReGIS, etc.)
      expected = [ 64, 1, 2, 6, 9, 15, 18, 21, 22 ]
    elif self._args.expected_terminal == "iTerm2":
      # TODO: Determine which VT levels are completely supported an add 6, 62, 63, or 64.
      # I believe 18 means we support DECSTB and DECSLRM but I can't find any
      # evidence to substantiate this belief.
      expected = [ 1, 2, 18, 22 ]
    AssertEQ(params, expected)

  def test_DA_NoParameter(self):
    esccsi.CSI_DA()
    self.handleDAResponse()

  def test_DA_0(self):
    esccsi.CSI_DA(0)
    self.handleDAResponse()



