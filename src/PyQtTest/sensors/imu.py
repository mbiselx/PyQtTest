#!/usr/bin/env python3
'''
use the winsdk project to get access to the current device orientation

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''


from winsdk.windows.devices.sensors import OrientationSensor, SensorQuaternion
import math
__all__ = [
    'get_current_euler',
    'get_current_euler_deg'
]


__default_orientation_sensor = OrientationSensor.get_default()


def __get_current_quaternion() -> SensorQuaternion:
    '''get the current orientation in native quaternion form'''
    reading = __default_orientation_sensor.get_current_reading()
    return reading.quaternion


def __quaternion_to_euler(q: SensorQuaternion) -> 'tuple[float, float, float]':
    '''transform a SensorQuaternion to en euler angle tuple of (roll, pitch, yaw)'''
    roll = math.asin(2*(q.w*q.y - q.z*q.x))
    pitch = math.atan2(2*(q.w*q.x + q.y*q.z),
                       1-2*(q.x**2 + q.y**2)) - 3.1415926/2
    yaw = math.atan2(2*(q.w*q.z + q.x*q.y),
                     1-2*(q.y**2 + q.z**2))
    return (roll, pitch, yaw)


def get_current_euler() -> 'tuple[float, float, float]':
    '''get the current orientation in euler angle form (radians)'''
    return __quaternion_to_euler(__get_current_quaternion())


def get_current_euler_deg() -> 'tuple[float, float, float]':
    '''get the current orientation in euler angle form (degrees)'''
    return tuple(a*180/3.1415926 for a in get_current_euler())


def _main():
    '''
    demo loop to print current euler angles to terminal

    CTRL + C to quit
    '''
    try:
        while True:
            e = get_current_euler_deg()

            print('\t'.join(f'{i:4.2f}°' for i in e), end='\r')

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    _main()
