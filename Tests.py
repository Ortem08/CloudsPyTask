import os
import unittest
import shutil

from requests.exceptions import HTTPError

from CloudsHandler import CloudsHandler


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = CloudsHandler()

    def test_try_to_check_nonexistent_directory(self):
        with self.assertRaises(HTTPError):
            self.handler.check_google('NON_EXISTENT_DIR')
        with self.assertRaises(HTTPError):
            self.handler.check_yandex('NON_EXISTENT_DIR')

    def test_check_folder(self):
        self.handler.upload_google(
            is_folder='folder',
            path='Tests_Directory')
        self.handler.upload_yandex(
            is_folder='folder',
            path='Tests_Directory')

        self.assertEqual(2, len(self.handler.check_google(
            'Tests_Directory'
        )))
        self.assertEqual(4, len(self.handler.check_google(
            'Test_Dir2'
        )))

        self.assertEqual(2, len(self.handler.check_yandex(
            'Tests_Directory'
        )))
        self.assertEqual(4, len(self.handler.check_yandex(
            'Test_Dir2'
        )))

    def test_upload_folder(self):
        self.assertTrue(self.handler.upload_google(
            is_folder='folder',
            path='Tests_Directory'))
        self.assertTrue(self.handler.upload_yandex(
            is_folder='folder',
            path='Tests_Directory'))

    def test_upload_file(self):
        self.assertTrue(self.handler.upload_google(
            is_folder='file',
            path='Tests_Directory/Test_File.txt'))
        self.assertTrue(self.handler.upload_yandex(
            is_folder='file',
            path='Tests_Directory/Test_File.txt'))

    def test_try_download_nonexistent_folder(self):
        with self.assertRaises(HTTPError):
            self.handler.download_google(is_dir='folder',
                                         name='NON_EXISTENT_DIR')
        with self.assertRaises(HTTPError):
            self.handler.download_yandex(is_dir='folder',
                                         name='NON_EXISTENT_DIR')

    def test_try_download_nonexistent_file(self):
        with self.assertRaises(HTTPError):
            self.handler.download_google(is_dir='file',
                                         name='NON_EXISTENT_FILE')
        with self.assertRaises(HTTPError):
            self.handler.download_yandex(is_dir='file',
                                         name='NON_EXISTENT_FILE')

    def test_download_folder(self):
        self.handler.download_google(is_dir=True, name='2 Сем')
        count = 0
        for path in os.scandir('Downloads/2 Сем'):
            if path.is_file():
                count += 1
        self.assertEqual(5, count)
        shutil.rmtree('Downloads/2 Сем')

        self.handler.download_yandex(is_dir=True, name='2 Сем')
        count = 0
        for path in os.scandir('Downloads/2 Сем'):
            if path.is_file():
                count += 1
        self.assertEqual(5, count)
        shutil.rmtree('Downloads/2 Сем')

    def test_download_file(self):
        self.handler.download_google(is_dir=False, name='Story 2.docx')
        self.assertTrue(os.path.isfile('Downloads/Story 2.docx'))
        os.remove('Downloads/Story 2.docx')

        self.handler.download_yandex(is_dir=False, name='Story 2.docx')
        self.assertTrue(os.path.isfile('Downloads/Story 2.docx'))
        os.remove('Downloads/Story 2.docx')
