import unittest
from io import StringIO
from unittest.mock import patch
import filecmp
import socket
from client import GUI


class MyTestCase(unittest.TestCase):

    def test_packet_loss(self):
        pass

    def test_packet_corruption(self):
        # corrupting packets
        pass

    def test_isFile(self):
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
