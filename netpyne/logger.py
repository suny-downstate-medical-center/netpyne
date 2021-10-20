import logging
import sys

class Logger():
  '''
    The class we use to print out our logs throughout netpyne.

    The default level of logging verbosity python sets is logging.WARNING,
    but netpyne users are likely to want it more verbose - thus we set it to logging.INFO.

    The user can change the default logging levels with:
      import logging
      logging.getLogger('netpyne').setLevel(logging.WARNING)
    Meaningful levels are: logging.DEBUG, logging.INFO, logging.WARNING and logging.ERROR.

    The user can separately control whether additional timing statements are printed out via the
      specs.SimConfig({ timing: True/False })
    option.
  '''

  def __init__(self):
    self.netpyne_logger = logging.getLogger('netpyne')
    self.netpyne_logger.setLevel(logging.INFO)
    self.netpyne_logger.propagate = False

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))

    self.netpyne_logger.addHandler(console_handler)

  def debug(self, *args, **kwargs):
    self.netpyne_logger.debug(*args, **kwargs)

  def info(self, *args, **kwargs):
    self.netpyne_logger.info(*args, **kwargs)

  def warning(self, *args, **kwargs):
    self.netpyne_logger.warning(*args, **kwargs)

  # The methods we don't yet use.
  # See https://github.com/Neurosim-lab/netpyne/pull/623 for explanations.
  #
  # def timing(self, *args, **kwargs):
  #   from . import sim
  #   if sim.cfg.timing:
  #     self.netpyne_logger.info(*args, **kwargs)
  # 
  # def error(*args, **kwargs):
  #   self.netpyne_logger.error(*args, **kwargs)
  #
  # def exception(*args, **kwargs):
  #   self.netpyne_logger.exception(*args, **kwargs)
  #
  # def critical(*args, **kwargs):
  #   self.netpyne_logger.debug(*args, **kwargs)

logger = Logger()
