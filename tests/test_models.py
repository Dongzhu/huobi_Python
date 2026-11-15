import unittest
from huobi.model.market import *
from huobi.model.trade import *
from huobi.model.account import *
from huobi.model.generic import *
from huobi.model.wallet import *
from huobi.model.etf import *
from huobi.model.algo import *
from huobi.model.margin import *
from huobi.model.subuser import *
from huobi.utils import default_parse, default_parse_list_dict
from huobi.utils.json_parser import fill_obj
from huobi.constant import *


class TestCandlestick(unittest.TestCase):
    def test_default_init(self):
        c = Candlestick()
        self.assertEqual(c.id, 0)
        self.assertEqual(c.open, 0.0)
        self.assertEqual(c.close, 0.0)
        self.assertEqual(c.high, 0.0)
        self.assertEqual(c.low, 0.0)
        self.assertEqual(c.amount, 0.0)
        self.assertEqual(c.vol, 0.0)
        self.assertEqual(c.count, 0)

    def test_print_object(self):
        c = Candlestick()
        c.id = 12345
        c.open = 100.0
        c.close = 110.0
        c.print_object()


class TestPriceDepth(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "ts": 1234567890,
            "version": 1,
            "bids": [[100.0, 1.0], [99.0, 2.0]],
            "asks": [[101.0, 1.5], [102.0, 2.5]]
        }
        depth = PriceDepth.json_parse(data)
        self.assertEqual(depth.ts, 1234567890)
        self.assertEqual(depth.version, 1)
        self.assertEqual(len(depth.bids), 2)
        self.assertEqual(len(depth.asks), 2)
        self.assertEqual(depth.bids[0].price, 100.0)
        self.assertEqual(depth.bids[0].amount, 1.0)
        self.assertEqual(depth.asks[0].price, 101.0)

    def test_json_parse_empty(self):
        depth = PriceDepth.json_parse({})
        self.assertEqual(depth.bids, [])
        self.assertEqual(depth.asks, [])

    def test_print_object(self):
        data = {
            "ts": 123,
            "version": 1,
            "bids": [[100.0, 1.0]],
            "asks": [[101.0, 1.5]]
        }
        depth = PriceDepth.json_parse(data)
        depth.print_object()


class TestDepthEntry(unittest.TestCase):
    def test_json_parse(self):
        entry = DepthEntry.json_parse([100.0, 5.0])
        self.assertEqual(entry.price, 100.0)
        self.assertEqual(entry.amount, 5.0)


class TestMarketDetail(unittest.TestCase):
    def test_default_parse(self):
        data = {
            "amount": 1000.0,
            "open": 100.0,
            "close": 110.0,
            "high": 120.0,
            "low": 90.0,
            "count": 10,
            "vol": 5000.0
        }
        detail = default_parse(data, MarketDetail)
        self.assertEqual(detail.amount, 1000.0)
        self.assertEqual(detail.open, 100.0)
        self.assertEqual(detail.close, 110.0)
        self.assertEqual(detail.high, 120.0)
        self.assertEqual(detail.low, 90.0)
        self.assertEqual(detail.count, 10)
        self.assertEqual(detail.vol, 5000.0)


class TestMarketTicker(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "symbol": "btcusdt",
            "open": 100.0,
            "close": 110.0,
            "high": 120.0,
            "low": 90.0,
            "amount": 1000.0,
            "vol": 5000.0,
            "count": 10
        }
        ticker = fill_obj(data, MarketTicker)
        self.assertEqual(ticker.symbol, "btcusdt")
        self.assertEqual(ticker.open, 100.0)


class TestTrade(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "trade-id": 12345,
            "ts": 1234567890,
            "amount": 1.5,
            "price": 100.0,
            "direction": "buy"
        }
        trade = fill_obj(data, Trade)
        self.assertEqual(trade.trade_id, 12345)
        self.assertEqual(trade.amount, 1.5)
        self.assertEqual(trade.price, 100.0)


class TestOrder(unittest.TestCase):
    def test_default_init(self):
        order = Order()
        self.assertEqual(order.id, 0)
        self.assertEqual(order.symbol, "")
        self.assertEqual(order.account_id, 0)
        self.assertEqual(order.amount, 0.0)
        self.assertEqual(order.price, 0.0)

    def test_json_parse(self):
        data = {
            "id": 12345,
            "symbol": "btcusdt",
            "account-id": 67890,
            "amount": "1.5",
            "price": "100.0",
            "type": "buy-limit",
            "source": "api",
            "state": "submitted",
            "filled-amount": "0.5",
            "filled-cash-amount": "50.0",
            "filled-fees": "0.1"
        }
        order = Order.json_parse(data)
        self.assertEqual(order.id, 12345)
        self.assertEqual(order.symbol, "btcusdt")
        self.assertEqual(order.filled_amount, "0.5")
        self.assertEqual(order.filled_cash_amount, "50.0")
        self.assertEqual(order.filled_fees, "0.1")

    def test_json_parse_field_aliases(self):
        data = {
            "id": 12345,
            "field-amount": "0.5",
            "field-cash-amount": "50.0",
            "field-fees": "0.1"
        }
        order = Order.json_parse(data)
        self.assertEqual(order.filled_amount, "0.5")
        self.assertEqual(order.filled_cash_amount, "50.0")
        self.assertEqual(order.filled_fees, "0.1")

    def test_json_parse_list(self):
        data = [
            {"id": 1, "symbol": "btcusdt"},
            {"id": 2, "symbol": "ethusdt"}
        ]
        orders = Order.json_parse_list(data)
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].id, 1)
        self.assertEqual(orders[1].id, 2)

    def test_json_parse_list_empty(self):
        self.assertEqual(Order.json_parse_list([]), [])
        self.assertEqual(Order.json_parse_list(None), [])

    def test_print_object(self):
        order = Order()
        order.id = 123
        order.symbol = "btcusdt"
        order.print_object()


class TestAccountBalance(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "id": 12345,
            "type": "spot",
            "state": "working",
            "list": [
                {"currency": "btc", "type": "trade", "balance": "1.5"},
                {"currency": "usdt", "type": "frozen", "balance": "100.0"}
            ]
        }
        account = AccountBalance.json_parse(data)
        self.assertEqual(account.id, 12345)
        self.assertEqual(account.type, "spot")
        self.assertEqual(account.state, "working")
        self.assertEqual(len(account.list), 2)

    def test_json_parse_none(self):
        self.assertIsNone(AccountBalance.json_parse(None))

    def test_json_parse_list(self):
        data = [
            {"id": 1, "type": "spot", "list": []},
            {"id": 2, "type": "margin", "list": []}
        ]
        accounts = AccountBalance.json_parse_list(data)
        self.assertEqual(len(accounts), 2)

    def test_json_parse_list_empty(self):
        self.assertEqual(AccountBalance.json_parse_list([]), [])


class TestBalance(unittest.TestCase):
    def test_default_init(self):
        b = Balance()
        self.assertEqual(b.currency, "")
        self.assertEqual(b.balance, 0.0)


class TestAccount(unittest.TestCase):
    def test_default_init(self):
        a = Account()
        self.assertEqual(a.id, 0)


class TestSymbol(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "symbol": "btcusdt",
            "base-currency": "btc",
            "quote-currency": "usdt",
            "price-precision": 2,
            "amount-precision": 4,
            "state": "online"
        }
        symbol = fill_obj(data, Symbol)
        self.assertEqual(symbol.symbol, "btcusdt")
        self.assertEqual(symbol.base_currency, "btc")
        self.assertEqual(symbol.quote_currency, "usdt")


class TestChain(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "chain": "btc",
            "baseChain": "btc",
            "depositStatus": "allowed",
            "withdrawStatus": "allowed"
        }
        chain = fill_obj(data, Chain)
        self.assertEqual(chain.chain, "btc")
        self.assertEqual(chain.baseChain, "btc")


class TestDeposit(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "currency": "btc",
            "chain": "btc",
            "amount": "1.5",
            "address": "abc123",
            "tx-hash": "hash123",
            "state": "confirmed"
        }
        deposit = fill_obj(data, Deposit)
        self.assertEqual(deposit.currency, "btc")
        self.assertEqual(deposit.amount, "1.5")
        self.assertEqual(deposit.state, "confirmed")


class TestWithdraw(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "id": 123,
            "currency": "btc",
            "chain": "btc",
            "amount": "1.5",
            "address": "abc123",
            "fee": "0.001",
            "state": "confirmed"
        }
        withdraw = fill_obj(data, Withdraw)
        self.assertEqual(withdraw.id, 123)
        self.assertEqual(withdraw.currency, "btc")
        self.assertEqual(withdraw.amount, "1.5")


class TestFeeRate(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "symbol": "btcusdt",
            "maker-fee": "0.002",
            "taker-fee": "0.002"
        }
        feerate = fill_obj(data, FeeRate)
        self.assertEqual(feerate.symbol, "btcusdt")
        self.assertEqual(feerate.maker_fee, "0.002")


class TestMatchResult(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "id": 123,
            "symbol": "btcusdt",
            "order-id": 456,
            "price": "100.0",
            "filled-amount": "1.5",
            "filled-fees": "0.1",
            "role": "taker"
        }
        match = fill_obj(data, MatchResult)
        self.assertEqual(match.id, 123)
        self.assertEqual(match.symbol, "btcusdt")


class TestEtfSwapConfig(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "etf_name": "hb10",
            "max_create_amount": "1000",
            "min_create_amount": "1",
            "max_redeem_amount": "1000",
            "min_redeem_amount": "1"
        }
        config = fill_obj(data, EtfSwapConfig)
        self.assertEqual(config.etf_name, "hb10")


class TestSubuserApikeyGeneration(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "accessKey": "key123",
            "secretKey": "secret123",
            "note": "test"
        }
        obj = fill_obj(data, SubuserApikeyGeneration)
        self.assertEqual(obj.accessKey, "key123")
        self.assertEqual(obj.secretKey, "secret123")


class TestCandlestickEvent(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "ch": "market.btcusdt.kline.1min",
            "ts": 1234567890,
            "tick": {
                "id": 123,
                "open": 100.0,
                "close": 110.0
            }
        }
        event = default_parse(data, CandlestickEvent, Candlestick)
        self.assertEqual(event.ch, "market.btcusdt.kline.1min")


class TestTradeDetailEvent(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "ch": "market.btcusdt.trade.detail",
            "ts": 1234567890,
            "tick": {
                "id": 123,
                "data": [{"id": 1, "amount": 1.0, "price": 100.0, "direction": "buy"}]
            }
        }
        event = default_parse(data, TradeDetailEvent, Trade)
        self.assertEqual(event.ch, "market.btcusdt.trade.detail")


class TestOrderUpdateEvent(unittest.TestCase):
    def test_fill_obj(self):
        data = {
            "action": "push",
            "data": {
                "order-id": 123,
                "symbol": "btcusdt"
            }
        }
        event = default_parse(data, OrderUpdateEvent, OrderUpdate)
        self.assertIsNotNone(event)


class TestMbp(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "seqNum": 1,
            "bids": [[100.0, 1.0]],
            "asks": [[101.0, 1.5]]
        }
        mbp = Mbp.json_parse(data)
        self.assertIsNotNone(mbp)


class TestTradeClearing(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "symbol": "btcusdt",
            "orderId": 123,
            "price": "100.0"
        }
        tc = TradeClearing.json_parse(data)
        self.assertIsNotNone(tc)


class TestLoanInfo(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "currency": "btc",
            "interestRate": "0.001",
            "minLoanAmt": "0.001",
            "maxLoanAmt": "100",
            "loanableAmt": "50"
        }
        ino = fill_obj(data, LoanInfo)
        self.assertEqual(ino.currency, "btc")


class TestCrossMarginAccountBalance(unittest.TestCase):
    def test_json_parse(self):
        data = {
            "id": 123,
            "type": "cross-margin",
            "state": "working",
            "list": []
        }
        obj = CrossMarginAccountBalance.json_parse(data)
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
