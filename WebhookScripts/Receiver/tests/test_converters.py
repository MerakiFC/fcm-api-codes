import pytest
from datetime import datetime


from WebhookScripts.Receiver.src.converters import epoch_to_aest, epoch_to_utc_iso, utc_iso_to_epoch, \
    utc_iso_to_tz_offset
from WebhookScripts.Receiver.src.exceptions import ConverterExceptionError


def test_epoch_to_aest_with_valid_epoch_time_london_returns_datetime() -> None:
    epoch_time_london = 1632183600

    result = epoch_to_aest(epoch_time=epoch_time_london, timezone='Europe/London')

    assert isinstance(result, datetime)


def test_epoch_to_aest_with_valid_epoch_time_brisbane_returns_datetime() -> None:
    epoch_time_brisbane = 1632128400

    result = epoch_to_aest(epoch_time=epoch_time_brisbane)

    assert isinstance(result, datetime)


def test_epoch_to_aest_with_invalid_epoch_time_raises_type_error() -> None:
    invalid_epoch_time = "invalid_time"

    with pytest.raises(ConverterExceptionError):
        epoch_to_aest(epoch_time=invalid_epoch_time)


def test_epoch_to_utc_iso_with_valid_time_london_returns_str() -> None:
    epoch_time = 1632183600

    result = epoch_to_utc_iso(epoch_time=epoch_time)

    expected_result = "2021-09-21T00:20:00Z"

    assert result == expected_result


def test_epoch_to_utc_iso_with_invalid_epoch_time_raises_type_error() -> None:
    invalid_epoch_time = "invalid_time"

    with pytest.raises(ConverterExceptionError):
        epoch_to_aest(epoch_time=invalid_epoch_time)


def test_utc_iso_to_epoch_with_valid_utc_time_returns_int() -> None:
    utc_to_iso = '2021-09-21T00:20:00'

    result = utc_iso_to_epoch(utc_time_iso=utc_to_iso)

    expected_result = 1632180000

    assert result == expected_result


def test_utc_iso_to_epoch_with_invalid_type_utc_time_raises_exception() -> None:
    invalid_utc_time = 1

    with pytest.raises(ConverterExceptionError):
        utc_iso_to_epoch(utc_time_iso=invalid_utc_time)


def test_utc_iso_to_epoch_with_invalid_utc_time_raises_exception() -> None:
    invalid_utc_time = 'invalid'

    with pytest.raises(ConverterExceptionError):
        utc_iso_to_epoch(utc_time_iso=invalid_utc_time)


def test_utc_iso_to_tz_offset_with_valid_iso_utc_time_and_valid_offset_returns_str() -> None:
    iso_utc = '2021-09-21T00:20:00'
    offset = 1

    result = utc_iso_to_tz_offset(iso_utc=iso_utc, offset=offset)

    expected_result = "2021-09-21T01:20:00"

    assert result == expected_result


def test_utc_iso_to_tz_offset_with_valid_iso_utc_time_and_invalid_offset_raises_exception() -> None:
    iso_utc = '2021-09-21T00:20:00'
    offset = 'invalid_offset'

    with pytest.raises(ConverterExceptionError):
        utc_iso_to_tz_offset(iso_utc=iso_utc, offset=offset)


def test_utc_iso_to_tz_offset_with_invalid_iso_utc_time_and_invalid_offset_raises_exception() -> None:
    iso_utc = 'invalid_time'
    offset = 'invalid_offset'

    with pytest.raises(ConverterExceptionError):
        utc_iso_to_tz_offset(iso_utc=iso_utc, offset=offset)


def test_utc_iso_to_tz_offset_with_invalid_iso_utc_time_and_valid_offset_raises_exception() -> None:
    iso_utc = 'invalid_time'
    offset = 1

    with pytest.raises(ConverterExceptionError):
        utc_iso_to_tz_offset(iso_utc=iso_utc, offset=offset)
