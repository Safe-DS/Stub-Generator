from typing import Any

import pytest
from syrupy import SnapshotAssertion
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.types import SerializedData


class SdsStubExtension(SingleFileSnapshotExtension):
    _file_extension = "sdsstub"

    def serialize(self, data: str, **_kwargs: Any) -> SerializedData:
        return bytes(data, encoding="utf8")


@pytest.fixture()
def snapshot_sds_stub(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.use_extension(SdsStubExtension)
