from enum import Enum, auto
import enum

class PowerState(Enum):
  ON = auto()
  OFF = auto()

class SmartPlugClient():
  """
  Interface for all client's to smart plugs
  """
  def turn_on():
    raise NotImplementedError()

  def turn_off():
    raise NotImplementedError()

  def read():
    raise NotImplementedError()