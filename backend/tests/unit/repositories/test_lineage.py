from typing import cast
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from luml.repositories.lineage import LineageRepository
from luml.schemas.artifacts import ArtifactType
from sqlalchemy.ext.asyncio import AsyncSession

ORBIT_ID = UUID("0199c337-09f3-753e-9def-b27745e69be6")
ARTIFACT_ID = UUID("0199c337-09fa-7ff6-b1e7-fc89a65f8622")


class TestLineageRepository:
    @pytest.mark.asyncio
    async def test_get_or_create_node_fails_loudly_when_the_node_is_missing(
        self,
    ) -> None:
        mock_session = Mock(spec=AsyncSession)
        mock_session.execute = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=None)
        mock_session.flush = AsyncMock()
        artifact = Mock()
        artifact.id = ARTIFACT_ID
        artifact.name = "model"
        artifact.type = ArtifactType.MODEL
        artifact.collection_name = "Models"
        repository = LineageRepository(Mock())

        with pytest.raises(RuntimeError, match="Lineage node was not created"):
            await repository.get_or_create_node(
                ORBIT_ID, artifact, cast(AsyncSession, mock_session)
            )

        mock_session.execute.assert_awaited_once()
        mock_session.scalar.assert_awaited_once()
        mock_session.flush.assert_not_awaited()
