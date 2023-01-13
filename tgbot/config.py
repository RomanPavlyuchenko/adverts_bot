from pydantic import BaseSettings


class DefaultConfig(BaseSettings):
    class Config:
        # env_prefix = "main"
        env_file = ".env"
        env_file_encoding = "utf-8"


class TgBot(DefaultConfig):
    token: str
    admins: list[int]
    use_redis: bool
    qiwi_token: str


class DbConfig(DefaultConfig):
    password: str
    user: str
    name: str
    host: str = "127.0.0.1"

    class Config:
        env_prefix = "DB_"


class Settings(BaseSettings):
    tg: TgBot = TgBot()
    db: DbConfig = DbConfig()



wb_ads_status = {11: 'Приостановлено', 9: 'Активна', 8: 'Отказался', 7: 'Показы завершены'}