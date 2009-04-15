#!/usr/bin/python
#
# Copyright (C) 2009  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Chris Lumens <clumens@redhat.com>
#                    David Cantrell <dcantrell@redhat.com>
#

import _ped
import unittest

from baseclass import *

# One class per method, multiple tests per class.  For these simple methods,
# that seems like good organization.  More complicated methods may require
# multiple classes and their own test suite.
class DeviceNewTestCase(unittest.TestCase):
    def runTest(self):
        # You're not allowed to create a new Device object by hand.
        self.assertRaises(TypeError, _ped.Device)

class DeviceGetSetTestCase(RequiresDevice):
    def runTest(self):
        # All attributes should be readable, but none should be writeable.
        for attr in ["model", "path", "type", "sector_size", "phys_sector_size",
                     "length", "open_count", "read_only", "external_mode",
                     "dirty", "boot_dirty", "host", "did"]:
            self.assertNotEquals(getattr(self._device, attr), None)
            self.assertRaises(AttributeError, setattr, self._device, attr, 47)

class DeviceIsBusyTestCase(RequiresDevice):
    def runTest(self):
        # Devices aren't busy until they're mounted.
        self.assertFalse(self._device.is_busy())

# TODO:  need to figure out how to make a loopback device look mounted to
# libparted
#        self.mkfs()
#        self.doMount()
#        self.assertTrue(self._device.is_busy())

class DeviceOpenTestCase(RequiresDevice):
    def runTest(self):
        self.assertTrue(self._device.open())
        self.assertEquals(self._device.open_count, 1)
        self._device.close()

        # Not allowed to open a device that's already been opened for external
        # access, so test that now.
        self._device.begin_external_access()
        self.assertRaises(_ped.IOException, self._device.open)
        self._device.end_external_access()
        self.assertTrue(self._device.open())

        # You're allowed to open a device multiple times.  It's already been
        # opened once above.  Try to open it again and make sure the count is
        # is right.
        self.assertTrue(self._device.open())
        self.assertEquals(self._device.open_count, 2)
        self._device.close()
        self._device.close()

class DeviceCloseTestCase(RequiresDevice):
    def runTest(self):
        self._device.open()
        self.assertTrue(self._device.close())
        self.assertEquals(self._device.open_count, 0)

        # Not allowed to close a device that's already been opened for external
        # access, so test that now.
        self._device.open()
        self._device.begin_external_access()
        self.assertRaises(_ped.IOException, self._device.close)
        self._device.end_external_access()
        self.assertTrue(self._device.close())

        # Test opening a device multiple times and then closing it too many.
        self._device.open()
        self._device.open()
        self.assertEquals(self._device.open_count, 2)
        self._device.close()
        self.assertEquals(self._device.open_count, 1)
        self._device.close()
        self.assertEquals(self._device.open_count, 0)
        self.assertRaises(_ped.IOException, self._device.close)

class DeviceDestroyTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class DeviceCacheRemoveTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class DeviceBeginExternalAccessTestCase(RequiresDevice):
    def runTest(self):
        # First test external access on a device that's not open.
        self.assertEquals(self._device.external_mode, 0)
        self.assertTrue(self._device.begin_external_access())
        self.assertEquals(self._device.external_mode, 1)
        self.assertEquals(self._device.open_count, 0)

        # Now stop external access, open the device, and re-test.
        self._device.end_external_access()
        self._device.open()
        self.assertEquals(self._device.open_count, 1)
        self.assertTrue(self._device.begin_external_access())
        self.assertEquals(self._device.open_count, 1)
        self._device.end_external_access()
        self._device.close()

class DeviceEndExternalAccessTestCase(RequiresDevice):
    def runTest(self):
        # Attempt to end external access on a device that never had it begun.
        self.assertRaises(_ped.IOException, self._device.end_external_access)

        # Now test external access on a device that's not open.
        self._device.begin_external_access()
        self.assertEquals(self._device.external_mode, 1)
        self.assertEquals(self._device.open_count, 0)
        self.assertTrue(self._device.end_external_access())
        self.assertEquals(self._device.external_mode, 0)
        self.assertEquals(self._device.open_count, 0)

        # Now on a device that's open.
        self._device.open()
        self._device.begin_external_access()
        self.assertEquals(self._device.external_mode, 1)
        self.assertEquals(self._device.open_count, 1)
        self.assertTrue(self._device.end_external_access())
        self.assertEquals(self._device.external_mode, 0)
        self.assertEquals(self._device.open_count, 1)
        self._device.close()

class DeviceReadTestCase(unittest.TestCase):
    def runTest(self):
        # TODO
        self.fail("Unimplemented test case.")

class DeviceWriteTestCase(unittest.TestCase):
    def runTest(self):
        # TODO
        self.fail("Unimplemented test case.")

class DeviceSyncTestCase(RequiresDevice):
    def runTest(self):
        # Can't sync a device that's not open or is in external mode.
        self.assertRaises(_ped.IOException, self._device.sync)

        self._device.open()
        self._device.begin_external_access()
        self.assertRaises(_ped.IOException, self._device.sync)

        # But this call should work.
        self._device.end_external_access()
        self.assertTrue(self._device.sync())
        self._device.close()

class DeviceSyncFastTestCase(RequiresDevice):
    def runTest(self):
        # Can't sync a device that's not open or is in external mode.
        self.assertRaises(_ped.IOException, self._device.sync_fast)

        self._device.open()
        self._device.begin_external_access()
        self.assertRaises(_ped.IOException, self._device.sync_fast)

        # But this call should work.
        self._device.end_external_access()
        self.assertTrue(self._device.sync_fast())
        self._device.close()

class DeviceCheckTestCase(RequiresDevice):
    def runTest(self):
        self._device.open()
        self.assertEquals(self._device.check(0, 20), 20)
        self._device.close()

class DeviceGetConstraintTestCase(RequiresDevice):
    def runTest(self):
        # XXX: This test case would be a lot more useful testing on real
        # hardware with unusual sector sizes.
        self.assertTrue(isinstance(self._device.get_constraint(), _ped.Constraint))

class UnitFormatCustomByteTestCase(RequiresDevice):
    def runTest(self):
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_SECTOR), '0s')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_BYTE), '47B')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_KILOBYTE), '0.05kB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_MEGABYTE), '0.00MB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_GIGABYTE), '0.00GB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_TERABYTE), '0.00TB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_COMPACT), '47.0B')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_CYLINDER), '0cyl')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_CHS), '0,0,0')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_PERCENT), '0.04%')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_KIBIBYTE), '0.05kiB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_MEBIBYTE), '0.00MiB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_GIBIBYTE), '0.00GiB')
        self.assertEquals(self._device.unit_format_custom_byte(47, _ped.UNIT_TEBIBYTE), '0.00TiB')

class UnitFormatByteTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class UnitFormatCustomTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class UnitFormatTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class UnitParseTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class UnitParseCustomTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

class DeviceStrTestCase(unittest.TestCase):
    # TODO
    def runTest(self):
        self.fail("Unimplemented test case.")

# And then a suite to hold all the test cases for this module.
def suite():
    suite = unittest.TestSuite()
    suite.addTest(DeviceNewTestCase())
    suite.addTest(DeviceGetSetTestCase())
    suite.addTest(DeviceIsBusyTestCase())
    suite.addTest(DeviceOpenTestCase())
    suite.addTest(DeviceCloseTestCase())
    suite.addTest(DeviceDestroyTestCase())
    suite.addTest(DeviceCacheRemoveTestCase())
    suite.addTest(DeviceBeginExternalAccessTestCase())
    suite.addTest(DeviceEndExternalAccessTestCase())
    suite.addTest(DeviceReadTestCase())
    suite.addTest(DeviceWriteTestCase())
    suite.addTest(DeviceSyncTestCase())
    suite.addTest(DeviceSyncFastTestCase())
    suite.addTest(DeviceCheckTestCase())
    suite.addTest(DeviceGetConstraintTestCase())
    suite.addTest(UnitFormatCustomByteTestCase())
    suite.addTest(UnitFormatByteTestCase())
    suite.addTest(UnitFormatCustomTestCase())
    suite.addTest(UnitFormatTestCase())
    suite.addTest(UnitParseTestCase())
    suite.addTest(UnitParseCustomTestCase())
    suite.addTest(DeviceStrTestCase())
    return suite

s = suite()
unittest.TextTestRunner(verbosity=2).run(s)
