from unittest.mock import Mock

import pytest
import requests

from WebhookScripts.Receiver.app import WX_API_URL
from WebhookScripts.Receiver.src.exceptions import HTTPRequestExceptionError, ConverterExceptionError, \
    InvalidPayloadExceptionError
from WebhookScripts.Receiver.src.wxtask import event_to_wx, mv_alert_to_wx

valid_payload: dict = {
  "version": "0.1",
  "sharedSecret": "secret",
  "sentAt": "2021-10-01T09:27:29.615483Z",
  "organizationId": "2930418",
  "organizationName": "My organization",
  "organizationUrl": "https://dashboard.meraki.com/o/VjjsAd/manage/organization/overview",
  "networkId": "N_24329156",
  "networkName": "Main Office",
  "networkUrl": "https://n1.meraki.com//n//manage/nodes/list",
  "networkTags": [],
  "deviceSerial": "Q234-ABCD-5678",
  "deviceMac": "00:11:22:33:44:55",
  "deviceName": "My camera",
  "deviceUrl": "https://n1.meraki.com//n//manage/nodes/new_list/000000000000",
  "deviceTags": [ "tag1", "tag2" ],
  "deviceModel": "MV",
  "alertId": "0000000000000000",
  "alertType": "Motion detected",
  "alertTypeId": "motion_alert",
  "alertLevel": "informational",
  "occurredAt": "2018-02-11T00:00:00.123450Z",
  "alertData": {
      "imageUrl": "https://cataas.com/cat",
      "timestamp": 1563499479.547,
      "motionRecapEnabled": True,
      "motionDetectorAllowsRecap": True,
      "isSpyglass": False,
      "imageEnabled": True
  }
}


def test_event_to_wx_failure_post_response_404_raises_exception_error(monkeypatch) -> None:

    mock_response = Mock()
    mock_response.status_code = 404

    def mock_requests_post(url, **kwargs) -> Mock:
        assert url == WX_API_URL
        return mock_response

    monkeypatch.setattr(requests, "post", mock_requests_post)

    with pytest.raises(HTTPRequestExceptionError):
        event_to_wx(payload=valid_payload)


def test_event_to_wx_failure_no_post_response_raises_exception_error(monkeypatch) -> None:

    def mock_requests_post(url, **kwargs) -> None:
        return None

    monkeypatch.setattr(requests, "post", mock_requests_post)

    with pytest.raises(HTTPRequestExceptionError):
        event_to_wx(payload=valid_payload)


def test_event_to_wx_success_returns_dict(monkeypatch) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"created": "2022-10-01T09:27:29.647522Z"}

    def mock_requests_post(url, **kwargs) -> Mock:
        assert url == WX_API_URL
        return mock_response

    monkeypatch.setattr(requests, "post", mock_requests_post)

    result = event_to_wx(payload=valid_payload)

    expected_result = {"created": "2022-10-01T09:27:29.647522Z"}

    assert result == expected_result


def test_event_to_wx_with_invalid_payload_raises_exception_error() -> None:
    invalid_payload: dict = {
        "key": "someValue",
        "anotherKey": "this is bad"
    }

    with pytest.raises(InvalidPayloadExceptionError):
        event_to_wx(payload=invalid_payload)


def test_event_to_wx_with_somewhat_invalid_payload_raises_exception_error() -> None:
    some_valid_keys_payload: dict = {
        "occurredAt": "2018-02-11T00:00:00.123450Z",
        "anotherKey": "this is bad"
    }

    with pytest.raises(InvalidPayloadExceptionError):
        event_to_wx(payload=some_valid_keys_payload)


def test_event_to_wx_with_invalid_date_payload_raises_exception_error() -> None:
    broken_date_payload: dict = {
        "occurredAt": "broken-date",
        "deviceName": "someDevice",
        "alertType": "critical",
        "networkName": "someNetwork"
    }

    with pytest.raises(ConverterExceptionError):
        event_to_wx(payload=broken_date_payload)


# without Recap tests


def test_mv_alert_to_wx_without_recap_success_returns_dict(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 200
    mock_response_post.json.return_value = {"created": "2022-05-31T10:29:01.226141"}

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> Mock:
        return mock_response_post

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" not in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)
    result = mv_alert_to_wx(payload=valid_payload, is_recap=False)

    expected_result = {"created": "2022-05-31T10:29:01.226141"}

    assert result == expected_result


def test_mv_alert_to_wx_without_recap_failed_post_raises_exception(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 200
    mock_response_post.json.return_value = {"created": "2022-05-31T10:29:01.226141"}

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> None:
        return None

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" not in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)

    with pytest.raises(HTTPRequestExceptionError):
        mv_alert_to_wx(payload=valid_payload, is_recap=False)


def test_mv_alert_to_wx_without_recap_failed_post_response_code_is_not_200_raises_exception(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 404

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> Mock:
        return mock_response_post

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" not in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)

    with pytest.raises(HTTPRequestExceptionError):
        mv_alert_to_wx(payload=valid_payload, is_recap=False)


# with Recap tests


def test_mv_alert_to_wx_with_recap_success_returns_dict(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 200
    mock_response_post.json.return_value = {"created": "2022-05-31T10:29:01.226141"}

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> Mock:
        return mock_response_post

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)

    result = mv_alert_to_wx(payload=valid_payload, is_recap=True)

    expected_result = {"created": "2022-05-31T10:29:01.226141"}

    assert result == expected_result


def test_mv_alert_to_wx_with_recap_failed_post_raises_exception(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 200
    mock_response_post.json.return_value = {"created": "2022-05-31T10:29:01.226141"}

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> None:
        return None

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)

    with pytest.raises(HTTPRequestExceptionError):
        mv_alert_to_wx(payload=valid_payload, is_recap=True)


def test_mv_alert_to_wx_with_recap_failed_post_response_code_is_not_200_raises_exception(monkeypatch) -> None:
    mock_response_get = Mock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"url": "http://some_video_url/"}

    mock_response_post = Mock()
    mock_response_post.status_code = 404

    def mock_requests_get(url, **kwargs) -> Mock:
        return mock_response_get

    def mock_requests_post(url, **kwargs) -> Mock:
        return mock_response_post

    monkeypatch.setattr(requests, "get", mock_requests_get)
    monkeypatch.setattr(requests, "post", mock_requests_post)

    def mock_process_image_file(file_path: str) -> bytes:
        assert "recap" in file_path
        return b'Mock image data'

    monkeypatch.setattr('WebhookScripts.Receiver.src.wxtask.process_image_file', mock_process_image_file)

    with pytest.raises(HTTPRequestExceptionError):
        mv_alert_to_wx(payload=valid_payload, is_recap=True)
