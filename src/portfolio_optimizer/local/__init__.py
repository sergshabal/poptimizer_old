"""Load local copy of data and updates it."""

from portfolio_optimizer.local.legacy_dividends import get_legacy_dividends as legacy_dividends
from portfolio_optimizer.local.local_cpi import cpi as cpi
from portfolio_optimizer.local.local_index import index as index_history
from portfolio_optimizer.local.local_quotes import prices as prices_history
from portfolio_optimizer.local.local_quotes import volumes as volumes_history
from portfolio_optimizer.local.local_securities_info import security_info as security_info
