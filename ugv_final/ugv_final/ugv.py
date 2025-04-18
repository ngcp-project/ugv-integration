
# WARNING: THIS FILE IS AUTO-GENERATED. DO NOT MODIFY.

# This file was generated from ugv.idl
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


@idl.struct(
    member_annotations = {
        'object_distance': [idl.array([5])],
    }
)
class auto_ctrl:
    auto_en: bool = False
    heading_error: idl.float32 = 0.0
    object_distance: Sequence[idl.float32] = field(default_factory = idl.array_factory(idl.float32, [5]))
    obstacle_flag: bool = False
    latitude: idl.float32 = 0.0
    longitude: idl.float32 = 0.0

@idl.struct(
    member_annotations = {
        'arm_cmd': [idl.array([5])],
    }
)
class man_ctrl:
    linear_vel: idl.float32 = 0.0
    steer_cmd: idl.float32 = 0.0
    arm_cmd: Sequence[idl.float32] = field(default_factory = idl.array_factory(idl.float32, [5]))
    auto_en: bool = False

@idl.struct(
    member_annotations = {
        'gps_pos': [idl.array([2])],
    }
)
class logger:
    gps_pos: Sequence[idl.float32] = field(default_factory = idl.array_factory(idl.float32, [2]))
    battery_life: idl.float32 = 0.0
