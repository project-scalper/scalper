import logging

adapter = logging.Logger(__name__)
trade_logger = logging.Logger(__name__)

# Creating handlers
c_handler = logging.StreamHandler()  # console handler
f_handler = logging.FileHandler('./file.log', mode="a")  # file handle
t_handler = logging.FileHandler('./trades.log', mode='a')   # trade logger
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.WARN)
t_handler.setLevel(logging.INFO)

# Creating formats
c_format = logging.Formatter('%(asctime)s - %(message)s')
f_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
t_format = logging.Formatter('%(asctime)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
t_handler.setFormatter(t_format)


# Add handlers to the logger
adapter.addHandler(c_handler)
adapter.addHandler(f_handler)
trade_logger.addHandler(t_handler)
trade_logger.addHandler(c_handler)
