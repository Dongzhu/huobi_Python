import unittest
from unittest import mock
import json
from huobi.client.market import MarketClient
from huobi.client.trade import TradeClient
from huobi.client.account import AccountClient
from huobi.client.generic import GenericClient
from huobi.client.wallet import WalletClient
from huobi.constant import *
from huobi.model.market import Candlestick, PriceDepth, MarketTicker
from huobi.model.trade import Order
from huobi.model.account import AccountBalance, Balance


class TestMarketServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = MarketClient()

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_candlestick_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "ch": "market.btcusdt.kline.1min",
            "data": [
                {"id": 1609459200, "open": "28900.0", "close": "28950.0",
                 "high": "29000.0", "low": "28800.0", "amount": "100.5",
                 "vol": "2900000.0", "count": 50}
            ]
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_candlestick("btcusdt", CandlestickInterval.MIN1, 1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].open, "28900.0")
        self.assertEqual(result[0].close, "28950.0")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_pricedepth_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "ts": 1609459200000,
            "tick": {
                "bids": [[28900.0, 1.0], [28899.0, 2.0]],
                "asks": [[28901.0, 1.5], [28902.0, 2.5]]
            }
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_pricedepth("btcusdt", DepthStep.STEP0)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.bids), 2)
        self.assertEqual(len(result.asks), 2)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_market_detail_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "tick": {
                "amount": "1000.5",
                "open": "28900.0",
                "close": "28950.0",
                "high": "29000.0",
                "low": "28800.0",
                "count": 100,
                "vol": "29000000.0"
            }
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_market_detail("btcusdt")
        self.assertIsNotNone(result)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_market_trade_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "tick": {
                "data": [
                    {"id": 123, "ts": 1609459200000, "trade-id": 456,
                     "amount": "1.5", "price": "28900.0", "direction": "buy"}
                ]
            }
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_market_trade("btcusdt")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_market_tickers_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "data": [
                {"symbol": "btcusdt", "open": "28900.0", "close": "28950.0",
                 "high": "29000.0", "low": "28800.0", "amount": "1000.5",
                 "vol": "29000000.0", "count": 100}
            ]
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_market_tickers()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)


class TestTradeServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TradeClient(api_key="test_key", secret_key="test_secret")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_create_order_full_flow(self, mock_post):
        response_data = {"status": "ok", "data": "123456789"}
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_post.return_value = mock_response

        order_id = self.client.create_order(
            symbol="btcusdt", account_id=12345, order_type=OrderType.BUY_LIMIT,
            amount=1.0, price=28900.0, source=OrderSource.API
        )
        self.assertEqual(order_id, 123456789)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_create_order_error_response(self, mock_post):
        response_data = {
            "status": "error",
            "err-code": "order-creation-failed",
            "err-msg": "Insufficient balance"
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_post.return_value = mock_response

        from huobi.exception.huobi_api_exception import HuobiApiException
        with self.assertRaises(HuobiApiException):
            self.client.create_order(
                symbol="btcusdt", account_id=12345, order_type=OrderType.BUY_LIMIT,
                amount=1.0, price=28900.0, source=OrderSource.API
            )

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_order_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "data": {
                "id": 123456789,
                "symbol": "btcusdt",
                "account-id": 12345,
                "amount": "1.0",
                "price": "28900.0",
                "type": "buy-limit",
                "state": "filled",
                "filled-amount": "1.0",
                "filled-cash-amount": "28900.0",
                "filled-fees": "0.002"
            }
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        order = self.client.get_order(123456789)
        self.assertEqual(order.id, 123456789)
        self.assertEqual(order.symbol, "btcusdt")
        self.assertEqual(order.state, "filled")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_cancel_order_full_flow(self, mock_post):
        response_data = {"status": "ok", "data": "123456789"}
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_post.return_value = mock_response

        result = self.client.cancel_order("btcusdt", 123456789)
        self.assertEqual(result, 123456789)


class TestAccountServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = AccountClient(api_key="test_key", secret_key="test_secret")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_accounts_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "data": [
                {"id": 12345, "type": "spot", "state": "working"},
                {"id": 67890, "type": "margin", "state": "working"}
            ]
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        accounts = self.client.get_accounts()
        self.assertIsInstance(accounts, list)
        self.assertEqual(len(accounts), 2)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_balance_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "data": {
                "id": 12345,
                "type": "spot",
                "state": "working",
                "list": [
                    {"currency": "btc", "type": "trade", "balance": "1.5"},
                    {"currency": "usdt", "type": "trade", "balance": "10000.0"}
                ]
            }
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        balances = self.client.get_balance(12345)
        self.assertIsInstance(balances, list)
        self.assertEqual(len(balances), 2)


class TestGenericServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = GenericClient()

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_exchange_timestamp_full_flow(self, mock_get):
        response_data = {"status": "ok", "data": 1609459200000}
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        ts = self.client.get_exchange_timestamp()
        self.assertEqual(ts, 1609459200000)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_get_reference_currencies_full_flow(self, mock_get):
        response_data = {
            "status": "ok",
            "data": [
                {
                    "currency": "btc",
                    "chains": [
                        {
                            "chain": "btc",
                            "depositStatus": "allowed",
                            "withdrawStatus": "allowed",
                            "numOfConfirmations": 1,
                            "numOfFastConfirmations": 0
                        }
                    ]
                }
            ]
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_get.return_value = mock_response

        result = self.client.get_reference_currencies()
        self.assertIsInstance(result, list)


class TestWalletServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = WalletClient(api_key="test_key", secret_key="test_secret")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_create_withdraw_full_flow(self, mock_post):
        response_data = {"status": "ok", "data": "987654321"}
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_post.return_value = mock_response

        result = self.client.post_create_withdraw(
            address="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            amount=0.5, currency="btc", fee=0.001
        )
        self.assertEqual(result, 987654321)


class TestBatchOrderIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TradeClient(api_key="test_key", secret_key="test_secret")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_batch_create_order_full_flow(self, mock_post):
        response_data = {
            "status": "ok",
            "data": [
                {"order-id": 111, "client-order-id": "c1"},
                {"order-id": 222, "client-order-id": "c2"}
            ]
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(response_data)
        mock_post.return_value = mock_response

        order_configs = [
            {"symbol": "btcusdt", "account_id": 1, "order_type": OrderType.BUY_LIMIT,
             "amount": 0.1, "price": 28900.0, "source": OrderSource.API, "client_order_id": "c1"},
            {"symbol": "ethusdt", "account_id": 1, "order_type": OrderType.SELL_LIMIT,
             "amount": 1.0, "price": 600.0, "source": OrderSource.API, "client_order_id": "c2"}
        ]
        result = self.client.batch_create_order(order_configs)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)


class TestAlgoServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TradeClient(api_key="test_key", secret_key="test_secret")

    def test_create_order_param_check_limit(self):
        # Should not raise
        self.client.create_order_param_check(
            symbol="btcusdt", account_id=1, order_type=OrderType.BUY_LIMIT,
            amount=1.0, price=28900.0, source=OrderSource.API
        )

    def test_create_order_param_check_market_no_price(self):
        # Market order should not require price
        self.client.create_order_param_check(
            symbol="btcusdt", account_id=1, order_type=OrderType.BUY_MARKET,
            amount=1.0, price=None, source=OrderSource.API
        )

    def test_create_order_param_check_limit_missing_price(self):
        from huobi.exception.huobi_api_exception import HuobiApiException
        with self.assertRaises(HuobiApiException):
            self.client.create_order_param_check(
                symbol="btcusdt", account_id=1, order_type=OrderType.BUY_LIMIT,
                amount=1.0, price=None, source=OrderSource.API
            )


class TestFullTradingWorkflow(unittest.TestCase):
    """Test a complete trading workflow with mocked network calls."""

    def setUp(self):
        self.market_client = MarketClient()
        self.trade_client = TradeClient(api_key="test_key", secret_key="test_secret")
        self.account_client = AccountClient(api_key="test_key", secret_key="test_secret")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_full_workflow(self, mock_get):
        # Step 1: Get market data
        market_data = {
            "status": "ok",
            "tick": {"amount": "1000.5", "open": "28900.0", "close": "28950.0",
                     "high": "29000.0", "low": "28800.0", "count": 100, "vol": "29000000.0"}
        }
        mock_response = mock.Mock()
        mock_response.text = json.dumps(market_data)
        mock_get.return_value = mock_response

        detail = self.market_client.get_market_detail("btcusdt")
        self.assertIsNotNone(detail)

        # Step 2: Get account balance
        balance_data = {
            "status": "ok",
            "data": {"id": 12345, "type": "spot", "state": "working", "list": []}
        }
        mock_response2 = mock.Mock()
        mock_response2.text = json.dumps(balance_data)
        mock_get.return_value = mock_response2

        balances = self.account_client.get_balance(12345)
        self.assertIsInstance(balances, list)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_order_lifecycle(self, mock_get, mock_post):
        # Create order
        create_data = {"status": "ok", "data": "123456789"}
        mock_post.return_value = mock.Mock(text=json.dumps(create_data))

        order_id = self.trade_client.create_order(
            symbol="btcusdt", account_id=12345, order_type=OrderType.BUY_LIMIT,
            amount=0.01, price=28900.0, source=OrderSource.API
        )
        self.assertEqual(order_id, 123456789)

        # Get order status
        order_data = {
            "status": "ok",
            "data": {"id": 123456789, "symbol": "btcusdt", "state": "submitted",
                     "amount": "0.01", "price": "28900.0", "filled-amount": "0"}
        }
        mock_get.return_value = mock.Mock(text=json.dumps(order_data))

        order = self.trade_client.get_order(order_id)
        self.assertEqual(order.state, "submitted")

        # Cancel order
        cancel_data = {"status": "ok", "data": "123456789"}
        mock_post.return_value = mock.Mock(text=json.dumps(cancel_data))

        cancel_result = self.trade_client.cancel_order("btcusdt", order_id)
        self.assertEqual(cancel_result, 123456789)


if __name__ == "__main__":
    unittest.main()
