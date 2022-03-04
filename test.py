import binascii
import unittest
from io import StringIO
from unittest.mock import patch
import filecmp
import random
from client import GUI


class MyTestCase(unittest.TestCase):

    def test_packet_loss(self):
        pass

    def test_packet_corruption(self):
        # corrupting packets
        pac1 = bytes("hdhwdhw6677", encoding='utf8')
        pac1 = pac1 + (binascii.crc32(pac1) & 0xffffffff).to_bytes(32, 'big')
        pac2 = bytes("jehhh3333", encoding='utf8')
        pac2 = pac2 + (binascii.crc32(pac2) & 0xffffffff).to_bytes(32, 'big')
        pac3 = bytes("ehdheejjjj", encoding='utf8')
        pac3 = pac3 + (binascii.crc32(pac3) & 0xffffffff).to_bytes(32, 'big')

        # corrupting pack1
        raw = list(pac1)
        for i in range(0, random.randint(1, 3)):
            pos = random.randint(0, len(raw) - 1)
            raw[pos] = random.randint(0, 255)

        # the method corrupting_check returns -1 if corruption happened
        # the test below checking if corruption happened on pac1, we corrupted it and named
        # the corrupted packet "raw", so the method needs to return -1
        self.assertEqual(-1, GUI.corrupting_check(self, bytes(raw)))

        # pac2 isn't corrupted so it shouldn't return -1
        self.assertNotEqual(-1, GUI.corrupting_check(self, pac2))

        # corrupting pac3
        raw3 = list(pac3)
        for i in range(0, random.randint(1, 3)):
            pos = random.randint(0, len(raw3) - 1)
            raw3[pos] = random.randint(0, 255)

        # pack3 corrupted - the corrupted pack is raw3
        # the method should return -1
        self.assertEqual(-1, GUI.corrupting_check(self, bytes(raw3)))

    def test_file_transfer_succeeded(self):
        # check if the file received is the file sent
        """
        To run this test properly, follow the instructions:
        - when the login window pops up, enter name
        - in the commands textbox enter "file"
        - in the text textbox enter the file name you wish to check (from the files that exist)
        - afterwards you can exit the client's window
        - the file should be downloaded
        - now we'll check that the file downloaded is the same as the one we wanted to download
        """
        client_gui = GUI()
        tst_path = 'b1.pdf'  # the name of file we downloaded
        ref_path = 'Files/b1.pdf'
        self.assertTrue(filecmp.cmp(tst_path, ref_path, shallow=False))


if __name__ == '__main__':
    unittest.main()
