from os import getenv

DATABASE_CONNECTION_URI = ":".join(
    [
        "postgresql+psycopg2",
        f'//{getenv("POSTGRES_USER")}',
        f'{getenv("POSTGRES_PASSWORD")}@postgres',  # container name postgres
        f'5432/{getenv("POSTGRES_DB")}',
    ]
)
