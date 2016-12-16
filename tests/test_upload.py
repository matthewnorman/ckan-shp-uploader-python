import pytest
import upload
import os.path
import argparse
import tempfile

from unittest import mock
from urllib.error import URLError
from ckanapi import NotAuthorized

def test_valid_api_key():
    good_api_key = '11111111-1111-1111-1111-111111111111'
    assert upload.valid_api_key(arg=good_api_key) == good_api_key

    with pytest.raises(argparse.ArgumentTypeError):
        upload.valid_api_key(arg='thisshouldbeugly')


def test_check_preview_file():

    with tempfile.TemporaryDirectory() as temp_dir:
        filename = os.path.join(temp_dir, 'test.txt')
        with pytest.raises(argparse.ArgumentTypeError):
            upload.check_preview_file(filename=filename)
        with open(filename, 'w') as f:
            f.write('1\n')
            f.write('2\n')
            f.write('3\n')

        upload.check_preview_file(filename=filename)


def test_to_string():

    uploader = upload.Uploader()
    uploader.server_url = 'server'
    uploader.api_key = 'api'
    uploader.dataset_name = 'dataset'
    uploader.filename = 'filename'

    assert uploader.to_string() == 'server api dataset filename'


def test_url_exists():
    """
    We're just mocking everything to make sure that the code
    gets exercised.
    """

    with mock.patch('upload.urllib.request.urlopen') as url_patch:
        url_patch.return_value = 200
        upload.url_exists(url='https://www.google.com')

    # Check a ValueError return
    with mock.patch('upload.urllib.request.urlopen') as url_patch:
        url_patch.side_effect = ValueError
        with pytest.raises(argparse.ArgumentTypeError):
            upload.url_exists(url='https://www.google.com')

    # Check a URLError return
    with mock.patch('upload.urllib.request.urlopen') as url_patch:
        url_patch.side_effect = URLError(reason='because')
        with pytest.raises(argparse.ArgumentTypeError):
            upload.url_exists(url='https://www.google.com')


def test_uploader_delete(monkeypatch):

    uploader = upload.Uploader()
    fake_ckan_inst = mock.MagicMock()
    monkeypatch.setattr(uploader, 'ckan_inst', fake_ckan_inst)
    uploader.ckan_delete_dataset(dataset_id=1)

    fake_ckan_inst.action.package_delete.side_effect = NotAuthorized
    monkeypatch.setattr(uploader, 'ckan_inst', fake_ckan_inst)
    with pytest.raises(NotAuthorized):
        uploader.ckan_delete_dataset(dataset_id=1)


def test_uploader_purge(monkeypatch):

    uploader = upload.Uploader()
    fake_ckan_inst = mock.MagicMock()
    monkeypatch.setattr(uploader, 'ckan_inst', fake_ckan_inst)
    uploader.ckan_purge_dataset(dataset_id=1)

    fake_ckan_inst.call_action.side_effect = NotAuthorized
    monkeypatch.setattr(uploader, 'ckan_inst', fake_ckan_inst)
    with pytest.raises(NotAuthorized):
        uploader.ckan_purge_dataset(dataset_id=1)
