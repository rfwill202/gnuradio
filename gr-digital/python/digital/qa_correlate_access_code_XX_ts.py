#!/usr/bin/env python
#
# Copyright 2006,2007,2010,2011,2013,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#


from gnuradio import gr, gr_unittest, digital, blocks
import pmt

default_access_code = '\xAC\xDD\xA4\xE2\xF2\x8C\x20\xFC'

def string_to_1_0_list(s):
    r = []
    for ch in s:
        x = ord(ch)
        for i in range(8):
            t = (x >> i) & 0x1
            r.append(t)
    return r

def to_1_0_string(L):
    return ''.join([chr(x + ord('0')) for x in L])

class test_correlate_access_code_XX_ts(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001(self):
        payload = "test packet"     # payload length is 11 bytes
        header = "\x00\xd0\x00\xd0" # header contains packet length, twice (bit-swapped)
        packet = header + payload
        pad = (0,) * 64
        src_data = (0, 0, 1, 1, 1, 1, 0, 1, 1) + tuple(string_to_1_0_list(packet)) + pad
        expected = tuple(map(int, src_data[9+32:-len(pad)]))
        src = blocks.vector_source_b(src_data)
        op = digital.correlate_access_code_bb_ts("1011", 0, "sync")
        dst = blocks.vector_sink_b()
        self.tb.connect(src, op, dst)
        self.tb.run()
        result_data = dst.data()
        result_tags = dst.tags()
        self.assertEqual(len(result_data), len(payload)*8)
        self.assertEqual(result_tags[0].offset, 0)
        self.assertEqual(pmt.to_long(result_tags[0].value), len(payload)*8)
        self.assertEqual(result_data, expected)

    def test_002(self):
        payload = "test packet"     # payload length is 11 bytes
        header = "\x00\xd0\x00\xd0" # header contains packet length, twice (bit-swapped)
        packet = header + payload
        pad = (0,) * 64
        src_data = (0, 0, 1, 1, 1, 1, 0, 1, 1) + tuple(string_to_1_0_list(packet)) + pad
        src_floats = tuple(2*b-1 for b in src_data) # convert to binary antipodal symbols (-1,1)
        expected = src_floats[9+32:-len(pad)]
        src = blocks.vector_source_f(src_floats)
        op = digital.correlate_access_code_ff_ts("1011", 0, "sync")
        dst = blocks.vector_sink_f()
        self.tb.connect(src, op, dst)
        self.tb.run()
        result_data = dst.data()
        result_tags = dst.tags()
        self.assertEqual(len(result_data), len(payload)*8)
        self.assertEqual(result_tags[0].offset, 0)
        self.assertEqual(pmt.to_long(result_tags[0].value), len(payload)*8)
        self.assertFloatTuplesAlmostEqual(result_data, expected, 5)


if __name__ == '__main__':
    gr_unittest.run(test_correlate_access_code_XX_ts, "test_correlate_access_code_XX_ts.xml")

