from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import iconeval
from iconeval import get_user_name

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mocked_getuid(mocker: MockerFixture) -> None:
    mocked_os = mocker.patch.object(iconeval, "os", autospec=True)
    mocked_os.getuid.return_value = -31415


class MockedStructPasswd:
    def __init__(
        self,
        *,
        raise_on_pw_gecos: bool = False,
        raise_on_pw_name: bool = False,
    ) -> None:
        self.raise_on_pw_gecos = raise_on_pw_gecos
        self.raise_on_pw_name = raise_on_pw_name

    @property
    def pw_gecos(self) -> str:
        if self.raise_on_pw_gecos:
            raise KeyError
        return "User of ICONEval, iconevaluser"

    @property
    def pw_name(self) -> str:
        if self.raise_on_pw_name:
            raise KeyError
        return "iconevaluser"


@pytest.fixture
def mocked_getpwuid(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(iconeval, "pwd", autospec=True)


@pytest.mark.parametrize("uid", [-27182, None])
def test_get_user_name_full_name(uid: int | None, mocker: MockerFixture) -> None:
    mocked_pwd = mocker.patch.object(iconeval, "pwd", autospec=True)
    mocked_pwd.getpwuid.return_value = MockedStructPasswd()
    user_name = get_user_name(uid)
    assert user_name == "User of ICONEval"


@pytest.mark.parametrize("uid", [-27182, None])
def test_get_user_name_user_name(uid: int | None, mocker: MockerFixture) -> None:
    mocked_pwd = mocker.patch.object(iconeval, "pwd", autospec=True)
    mocked_pwd.getpwuid.return_value = MockedStructPasswd(raise_on_pw_gecos=True)
    user_name = get_user_name(uid)
    assert user_name == "iconevaluser"


@pytest.mark.parametrize("uid", [-27182, None])
def test_get_user_name_uid(uid: int | None, mocker: MockerFixture) -> None:
    mocked_pwd = mocker.patch.object(iconeval, "pwd", autospec=True)
    mocked_pwd.getpwuid.return_value = MockedStructPasswd(
        raise_on_pw_gecos=True,
        raise_on_pw_name=True,
    )
    user_name = get_user_name(uid)
    if uid is None:
        assert user_name == "UID: -31415"
    else:
        assert user_name == "UID: -27182"
