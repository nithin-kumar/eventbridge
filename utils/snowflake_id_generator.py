from snowflake import SnowflakeGenerator


class SnowflakeIDGeneratorSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SnowflakeIDGeneratorSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.snowflake_id_generator = SnowflakeGenerator(42)
        return cls._instance

    def get_snowflake_id(self):
        return next(self.snowflake_id_generator)
