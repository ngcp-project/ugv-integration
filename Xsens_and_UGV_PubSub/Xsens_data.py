
# WARNING: THIS FILE IS AUTO-GENERATED. DO NOT MODIFY.

# This file was generated from Xsens_data.idl
# using RTI Code Generator (rtiddsgen) version 4.3.0.
# The rtiddsgen tool is part of the RTI Connext DDS distribution.
# For more information, type 'rtiddsgen -help' at a command shell
# or consult the Code Generator User's Manual.

from dataclasses import field
from typing import Union, Sequence, Optional
import rti.idl as idl
from enum import IntEnum
import sys
import os


@idl.struct
class Xsens_data:
    timestamp: float = 0.0
    accel_x: idl.float32 = 0.0
    accel_y: idl.float32 = 0.0
    accel_z: idl.float32 = 0.0
    gyro_x: idl.float32 = 0.0
    gyro_y: idl.float32 = 0.0
    gyro_z: idl.float32 = 0.0
    roll: idl.float32 = 0.0
    pitch: idl.float32 = 0.0
    yaw: idl.float32 = 0.0
    latitude: float = 0.0
    longitude: float = 0.0

@idl.struct
class ugv_data:
    goal_heading: idl.float32 = 0.0
    actual_heading: idl.float32 = 0.0
    error_heading: idl.float32 = 0.0
