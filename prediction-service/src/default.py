db_default = {
    'MOTOR_URI': 'mongodb://ga-service:ga-service@localhost:27018/sensors?authSource=admin',
    'DB_INDIVIDUALS': 'individuals',
    'DB_CONFIG': 'config',
    'DB_DATA': 'data',
}


def safe_load_default(cfg: dict):
    if not any(db_param in cfg.keys() for db_param in db_default.keys()):
        cfg.update(db_default)
