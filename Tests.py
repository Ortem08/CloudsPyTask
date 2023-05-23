import unittest

from googleapiclient.errors import HttpError

from CloudsHandler import CloudsHandler


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = CloudsHandler()

    def test_try_to_check_nonexistent_directory(self):
        with self.assertRaises(NotImplementedError):
            self.handler.check_google('NON_EXISTENT_DIR')

    def test_check_test_folder_google(self):
        self.handler.upload_google(
            is_folder='folder',
            path='Tests_Directory')

        self.assertEqual(2, len(self.handler.check_google(
            'Tests_Directory'
        )))
        self.assertEqual(4, len(self.handler.check_google(
            'Test_Dir2'
        )))

    def test_upload_folder_google(self):
        self.assertEqual(True, self.handler.upload_google(
            is_folder='folder',
            path='Tests_Directory')
            )

    def test_upload_file_google(self):
        self.assertEqual(True, self.handler.upload_google(
            is_folder='file',
            path='Tests_Directory/Test_File.txt')
            )

    def test_try_download_nonexistent_folder_google(self):
        with self.assertRaises(NotImplementedError):
            self.handler.download_google(is_dir='folder',
                                         name='NON_EXISTENT_DIR')

    def test_try_download_nonexistent_file_google(self):
        with self.assertRaises(NotImplementedError):
            self.handler.download_google(is_dir='file',
                                         name='NON_EXISTENT_FILE')


