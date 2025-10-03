"""Id to uuid7

Revision ID: 020
Revises: 019
Create Date: 2025-10-02 21:30:48.186512

"""
from typing import Sequence, Optional
from datetime import datetime
import secrets

from alembic import op
import sqlalchemy as sa
import uuid6


# revision identifiers, used by Alembic.
revision: str = '020'
down_revision: str | None = '019'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid7_from_datetime(dt: Optional[datetime] = None) -> uuid6.UUID:
    """
    Генерирует UUID7 с кастомной датой
    """
    if dt is None:
        dt = datetime.now()
    
    timestamp_ms = int(dt.timestamp() * 1000)
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80  # 48 bit timestamp
    uuid_int |= secrets.randbits(76)  # 76 random bits

    return uuid6.UUID(int=uuid_int, version=7)


def upgrade() -> None:
    # Таблицы и их UUID поля для обновления
    tables_to_update = [
        ('users', ['id']),
        ('organizations', ['id']),
        ('organization_members', ['id', 'user_id', 'organization_id']),
        ('organization_invites', ['id', 'organization_id', 'invited_by']),
        ('orbits', ['id', 'organization_id', 'bucket_secret_id']),
        ('orbit_members', ['id', 'user_id', 'orbit_id']),
        ('satellites', ['id', 'orbit_id']),
        ('satellite_queue', ['id', 'satellite_id', 'orbit_id']),
        ('deployments', ['id', 'orbit_id', 'satellite_id', 'model_id']),
        ('collections', ['id', 'orbit_id']),
        ('orbit_secrets', ['id', 'orbit_id']),
        ('bucket_secrets', ['id', 'organization_id']),
        ('model_artifacts', ['id', 'collection_id']),
        ('token_black_list', ['id']),
        ('stats_emails', ['id'])
    ]

    # Мапинг старых UUID -> новых UUID7 для каждой таблицы
    uuid_mappings = {}
    connection = op.get_bind()

    # Шаг 1: Обновляем primary keys (id столбцы)
    for table_name, uuid_columns in tables_to_update:
        print(f"Processing primary keys for table: {table_name}")
        
        # Добавляем временный столбец для нового UUID7
        op.add_column(table_name, sa.Column('new_id', sa.UUID(), nullable=True))
        
        # Получаем все записи с их created_at
        if table_name == 'token_black_list':
            # У token_black_list нет created_at
            query = sa.text(f"SELECT id FROM {table_name}")
            result = connection.execute(query)
            rows = [(row[0], datetime.now()) for row in result]
        else:
            query = sa.text(f"SELECT id, created_at FROM {table_name}")
            result = connection.execute(query)
            rows = [(row[0], row[1]) for row in result]
        
        # Генерируем UUID7 для каждой записи и сохраняем мапинг
        table_mapping = {}
        for old_id, created_at in rows:
            new_uuid7 = uuid7_from_datetime(created_at)
            table_mapping[str(old_id)] = str(new_uuid7)
            
            # Обновляем запись
            update_query = sa.text(f"""
                UPDATE {table_name} 
                SET new_id = :new_id 
                WHERE id = :old_id
            """)
            connection.execute(update_query, {
                'new_id': str(new_uuid7),
                'old_id': str(old_id)
            })
        
        uuid_mappings[table_name] = table_mapping

    # Шаг 2: Обновляем foreign keys
    foreign_key_updates = [
        ('organization_members', 'user_id', 'users'),
        ('organization_members', 'organization_id', 'organizations'),
        ('organization_invites', 'organization_id', 'organizations'),
        ('organization_invites', 'invited_by', 'users'),
        ('orbits', 'organization_id', 'organizations'),
        ('orbits', 'bucket_secret_id', 'bucket_secrets'),
        ('orbit_members', 'user_id', 'users'),
        ('orbit_members', 'orbit_id', 'orbits'),
        ('satellites', 'orbit_id', 'orbits'),
        ('satellite_queue', 'satellite_id', 'satellites'),
        ('satellite_queue', 'orbit_id', 'orbits'),
        ('deployments', 'orbit_id', 'orbits'),
        ('deployments', 'satellite_id', 'satellites'),
        ('deployments', 'model_id', 'model_artifacts'),
        ('collections', 'orbit_id', 'orbits'),
        ('orbit_secrets', 'orbit_id', 'orbits'),
        ('bucket_secrets', 'organization_id', 'organizations'),
        ('model_artifacts', 'collection_id', 'collections'),
    ]

    for table_name, fk_column, ref_table in foreign_key_updates:
        print(f"Processing foreign key: {table_name}.{fk_column} -> {ref_table}")
        
        # Добавляем временный столбец для нового FK
        op.add_column(table_name, sa.Column(f'new_{fk_column}', sa.UUID(), nullable=True))
        
        # Обновляем FK используя мапинг
        ref_mapping = uuid_mappings[ref_table]
        for old_uuid, new_uuid in ref_mapping.items():
            update_query = sa.text(f"""
                UPDATE {table_name}
                SET new_{fk_column} = :new_uuid
                WHERE {fk_column} = :old_uuid
            """)
            connection.execute(update_query, {
                'new_uuid': new_uuid,
                'old_uuid': old_uuid
            })

    # Шаг 3: Удаляем старые столбцы и переименовываем новые
    # Сначала удаляем все foreign key constraints
    op.execute("SET session_replication_role = replica;")  # Отключаем FK проверки
    
    for table_name, uuid_columns in tables_to_update:
        print(f"Replacing columns for table: {table_name}")
        
        for col in uuid_columns:
            # Удаляем старый столбец
            op.drop_column(table_name, col)
            # Переименовываем новый столбец
            op.alter_column(table_name, f'new_{col}', new_column_name=col, nullable=False)

    # Включаем FK проверки обратно
    op.execute("SET session_replication_role = DEFAULT;")

    # Шаг 4: Пересоздаем constraints
    for table_name, uuid_columns in tables_to_update:
        if 'id' in uuid_columns:
            try:
                op.create_primary_key(f'pk_{table_name}', table_name, ['id'])
            except Exception:
                pass  # PK может уже существовать

    # Пересоздаем foreign key constraints
    fk_constraints = [
        ('organization_members', 'user_id', 'users', 'id'),
        ('organization_members', 'organization_id', 'organizations', 'id'),
        ('organization_invites', 'organization_id', 'organizations', 'id'),
        ('organization_invites', 'invited_by', 'users', 'id'),
        ('orbits', 'organization_id', 'organizations', 'id'),
        ('orbits', 'bucket_secret_id', 'bucket_secrets', 'id'),
        ('orbit_members', 'user_id', 'users', 'id'),
        ('orbit_members', 'orbit_id', 'orbits', 'id'),
        ('satellites', 'orbit_id', 'orbits', 'id'),
        ('satellite_queue', 'satellite_id', 'satellites', 'id'),
        ('satellite_queue', 'orbit_id', 'orbits', 'id'),
        ('deployments', 'orbit_id', 'orbits', 'id'),
        ('deployments', 'satellite_id', 'satellites', 'id'),
        ('deployments', 'model_id', 'model_artifacts', 'id'),
        ('collections', 'orbit_id', 'orbits', 'id'),
        ('orbit_secrets', 'orbit_id', 'orbits', 'id'),
        ('bucket_secrets', 'organization_id', 'organizations', 'id'),
        ('model_artifacts', 'collection_id', 'collections', 'id'),
    ]

    for table_name, fk_column, ref_table, ref_column in fk_constraints:
        try:
            op.create_foreign_key(
                f'fk_{table_name}_{fk_column}',
                table_name, ref_table,
                [fk_column], [ref_column],
                ondelete='CASCADE'
            )
        except Exception:
            pass  # FK может уже существовать

    print("UUID4 -> UUID7 migration completed successfully!")


def downgrade() -> None:
    raise NotImplementedError("Downgrade from UUID7 to UUID4 is not supported")