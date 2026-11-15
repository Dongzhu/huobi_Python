import unittest
from unittest import mock
from huobi.client.market import MarketClient
from huobi.client.trade import TradeClient
from huobi.client.account import AccountClient
from huobi.client.wallet import WalletClient
from huobi.client.generic import GenericClient
from huobi.client.margin import MarginClient
from huobi.client.etf import EtfClient
from huobi.client.algo import AlgoClient
from huobi.client.subuser import SubuserClient
from huobi.constant import *
from huobi.exception.huobi_api_exception import HuobiApiException


class TestMarketClient(unittest.TestCase):
    def setUp(self):
        self.client = MarketClient()

    @mock.patch("huobi.service.market.get_candlestick.GetCandleStickService.request")
    def test_get_candlestick(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_candlestick("btcusdt", CandlestickInterval.MIN5, 10)
        self.assertEqual(result, [])
        mock_request.assert_called_once()

    def test_get_candlestick_invalid_symbol(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_candlestick(123, CandlestickInterval.MIN5, 10)

    def test_get_candlestick_invalid_size(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_candlestick("btcusdt", CandlestickInterval.MIN5, 3000)

    def test_get_candlestick_none_period(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_candlestick("btcusdt", None, 10)

    @mock.patch("huobi.service.market.get_pricedepth.GetPriceDepthService.request")
    def test_get_pricedepth(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_pricedepth("btcusdt", DepthStep.STEP0)
        self.assertIsNone(result)

    def test_get_pricedepth_invalid_step(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_pricedepth("btcusdt", "invalid")

    @mock.patch("huobi.service.market.get_market_detail.GetMarketDetailService.request")
    def test_get_market_detail(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_market_detail("btcusdt")
        self.assertIsNone(result)

    @mock.patch("huobi.service.market.get_market_trade.GetMarketTradeService.request")
    def test_get_market_trade(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_market_trade("btcusdt")
        self.assertEqual(result, [])

    @mock.patch("huobi.service.market.get_history_trade.GetHistoryTradeService.request")
    def test_get_history_trade(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_history_trade("btcusdt", 10)
        self.assertEqual(result, [])

    @mock.patch("huobi.service.market.get_market_tickers.GetMarketTickersService.request")
    def test_get_market_tickers(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_market_tickers()
        self.assertEqual(result, [])

    def test_get_depth_step_list(self):
        steps = MarketClient.get_depth_step_list()
        self.assertEqual(len(steps), 6)

    def test_get_valid_depth_step_valid(self):
        self.assertEqual(MarketClient.get_valid_depth_step(DepthStep.STEP1, DepthStep.STEP0), DepthStep.STEP1)

    def test_get_valid_depth_step_invalid(self):
        self.assertEqual(MarketClient.get_valid_depth_step("invalid", DepthStep.STEP0), DepthStep.STEP0)


class TestTradeClient(unittest.TestCase):
    def setUp(self):
        self.client = TradeClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.trade.get_order_by_id.GetOrderByIdService.request")
    def test_get_order(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_order(12345)
        self.assertIsNone(result)

    def test_get_order_none_id(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_order(None)

    @mock.patch("huobi.service.trade.post_create_order.PostCreateOrderService.request")
    def test_create_order(self, mock_request):
        mock_request.return_value = 12345
        result = self.client.create_order(
            symbol="btcusdt", account_id=1, order_type=OrderType.BUY_LIMIT,
            amount=1.0, price=100.0, source=OrderSource.API
        )
        self.assertEqual(result, 12345)

    def test_create_order_missing_price(self):
        with self.assertRaises(HuobiApiException):
            self.client.create_order(
                symbol="btcusdt", account_id=1, order_type=OrderType.BUY_LIMIT,
                amount=1.0, price=None, source=OrderSource.API
            )

    @mock.patch("huobi.service.trade.post_cancel_order.PostCancelOrderService.request")
    def test_cancel_order(self, mock_request):
        mock_request.return_value = 12345
        result = self.client.cancel_order("btcusdt", 12345)
        self.assertEqual(result, 12345)

    @mock.patch("huobi.service.trade.post_batch_cancel_order.PostBatchCancelOrderService.request")
    def test_cancel_orders(self, mock_request):
        mock_request.return_value = None
        result = self.client.cancel_orders("btcusdt", [1, 2, 3])
        self.assertIsNone(result)

    def test_cancel_orders_empty_list(self):
        with self.assertRaises(HuobiApiException):
            self.client.cancel_orders("btcusdt", [])

    @mock.patch("huobi.service.trade.get_orders.GetOrdersService.request")
    def test_get_orders(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_orders("btcusdt", OrderState.SUBMITTED)
        self.assertEqual(result, [])

    @mock.patch("huobi.service.trade.get_open_orders.GetOpenOrdersService.request")
    def test_get_open_orders(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_open_orders("btcusdt", 123)
        self.assertEqual(result, [])

    @mock.patch("huobi.service.trade.get_match_results.GetMatchResultsService.request")
    def test_get_match_result(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_match_result("btcusdt")
        self.assertEqual(result, [])

    @mock.patch("huobi.service.trade.post_batch_create_order.PostBatchCreateOrderService.request")
    def test_batch_create_order(self, mock_request):
        mock_request.return_value = [1, 2]
        order_configs = [
            {"symbol": "btcusdt", "account_id": 1, "order_type": OrderType.BUY_LIMIT,
             "amount": 1.0, "price": 100.0, "source": OrderSource.API}
        ]
        result = self.client.batch_create_order(order_configs)
        self.assertEqual(result, [1, 2])

    def test_batch_create_order_empty(self):
        with self.assertRaises(HuobiApiException):
            self.client.batch_create_order([])

    def test_order_source_desc_spot(self):
        self.assertEqual(self.client.order_source_desc(None), "api")

    def test_order_source_desc_margin(self):
        self.assertEqual(self.client.order_source_desc(AccountType.MARGIN), "margin-api")


class TestAccountClient(unittest.TestCase):
    def setUp(self):
        self.client = AccountClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.account.get_accounts.GetAccountsService.request")
    def test_get_accounts(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_accounts()
        self.assertEqual(result, [])

    @mock.patch("huobi.service.account.get_balance.GetBalanceService.request")
    def test_get_balance(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_balance(12345)
        self.assertEqual(result, [])

    def test_get_balance_none_id(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_balance(None)

    @mock.patch("huobi.service.account.get_account_balance_by_subuid.GetAccountBalanceBySubUidService.request")
    def test_get_account_balance_by_subuid(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_account_balance_by_subuid(12345)
        self.assertIsNone(result)

    def test_get_account_balance_by_subuid_none(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_account_balance_by_subuid(None)

    @mock.patch("huobi.service.account.get_account_history.GetAccountHistoryService.request")
    def test_get_account_history(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_account_history(12345)
        self.assertEqual(result, [])

    def test_get_account_history_none_account_id(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_account_history(None)

    @mock.patch("huobi.service.account.get_account_asset_valuation.GetAccountAssetValuationService.request")
    def test_get_account_asset_valuation(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_account_asset_valuation(AccountType.SPOT)
        self.assertIsNone(result)

    def test_get_account_asset_valuation_none_type(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_account_asset_valuation(None)

    @mock.patch("huobi.service.account.get_account_point.GetAccountPointService.request")
    def test_get_account_point(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_account_point()
        self.assertIsNone(result)


class TestWalletClient(unittest.TestCase):
    def setUp(self):
        self.client = WalletClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.wallet.get_deposit_withdraw.GetDepositWithdrawService.request")
    def test_get_deposit_withdraw(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_deposit_withdraw(DepositWithdraw.DEPOSIT)
        self.assertEqual(result, [])

    def test_get_deposit_withdraw_none_op_type(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_deposit_withdraw(None)

    @mock.patch("huobi.service.wallet.post_create_withdraw.PostCreateWithdrawService.request")
    def test_post_create_withdraw(self, mock_request):
        mock_request.return_value = 12345
        result = self.client.post_create_withdraw(
            address="abc", amount=1.0, currency="btc", fee=0.001
        )
        self.assertEqual(result, 12345)

    def test_post_create_withdraw_missing_params(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_create_withdraw(address=None, amount=1.0, currency="btc", fee=0.001)

    @mock.patch("huobi.service.wallet.post_cancel_withdraw.PostCancelWithdrawService.request")
    def test_post_cancel_withdraw(self, mock_request):
        mock_request.return_value = 12345
        result = self.client.post_cancel_withdraw(12345)
        self.assertEqual(result, 12345)

    @mock.patch("huobi.service.wallet.get_account_deposit_address.GetAccountDepositAddressService.request")
    def test_get_account_deposit_address(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_account_deposit_address("btc")
        self.assertEqual(result, [])

    def test_get_account_deposit_address_none(self):
        with self.assertRaises(HuobiApiException):
            self.client.get_account_deposit_address(None)


class TestGenericClient(unittest.TestCase):
    def setUp(self):
        self.client = GenericClient()

    @mock.patch("huobi.service.generic.get_exchange_timestamp.GetExchangeTimestampService.request")
    def test_get_exchange_timestamp(self, mock_request):
        mock_request.return_value = 1234567890
        result = self.client.get_exchange_timestamp()
        self.assertEqual(result, 1234567890)

    @mock.patch("huobi.service.generic.get_exchange_symbols.GetExchangeSymbolsService.request")
    @mock.patch("huobi.service.generic.get_exchange_currencies.GetExchangeCurrenciesService.request")
    def test_get_exchange_info(self, mock_currencies, mock_symbols):
        mock_symbols.return_value = []
        mock_currencies.return_value = []
        result = self.client.get_exchange_info()
        self.assertIsNotNone(result)

    @mock.patch("huobi.service.generic.get_reference_currencies.GetReferenceCurrenciesService.request")
    def test_get_reference_currencies(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_reference_currencies()
        self.assertEqual(result, [])


class TestMarginClient(unittest.TestCase):
    def setUp(self):
        self.client = MarginClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.margin.post_transfer_in_margin.PostTransferInMarginService.request")
    def test_post_transfer_in_margin(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_transfer_in_margin("btcusdt", "btc", 1.0)
        self.assertEqual(result, 123)

    @mock.patch("huobi.service.margin.post_create_margin_order.PostCreateMarginOrderService.request")
    def test_post_create_margin_order(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_create_margin_order("btcusdt", "btc", 1.0)
        self.assertEqual(result, 123)

    @mock.patch("huobi.service.margin.post_repay_margin_order.PostRepayMarginOrderService.request")
    def test_post_repay_margin_order(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_repay_margin_order(123, 1.0)
        self.assertEqual(result, 123)

    def test_post_repay_margin_order_none_loan_id(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_repay_margin_order(None, 1.0)


class TestEtfClient(unittest.TestCase):
    def setUp(self):
        self.client = EtfClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.etf.get_etf_swap_config.GetEtfSwapConfigService.request")
    def test_get_etf_swap_config(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_etf_swap_config("hb10")
        self.assertIsNone(result)

    @mock.patch("huobi.service.etf.post_etf_swap_in.PostEftSwapInService.request")
    def test_post_etf_swap_in(self, mock_request):
        mock_request.return_value = None
        result = self.client.post_etf_swap_in("hb10", 10)
        self.assertIsNone(result)

    def test_post_etf_swap_in_none_amount(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_etf_swap_in("hb10", None)


class TestAlgoClient(unittest.TestCase):
    def setUp(self):
        self.client = AlgoClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.algo.post_create_order.PostCreateOrderService.request")
    def test_create_order(self, mock_request):
        mock_request.return_value = 123
        result = self.client.create_order(
            account_id=1, symbol="btcusdt", order_side=OrderSide.BUY,
            order_type=AlgoOrderType.LIMIT, client_order_id="c1",
            stop_price="100", order_price="95", order_size="1"
        )
        self.assertEqual(result, 123)

    @mock.patch("huobi.service.algo.post_cancel_orders.PostCancelOrderService.request")
    def test_cancel_orders(self, mock_request):
        mock_request.return_value = None
        result = self.client.cancel_orders(["c1", "c2"])
        self.assertIsNone(result)

    def test_cancel_orders_none(self):
        with self.assertRaises(HuobiApiException):
            self.client.cancel_orders(None)

    @mock.patch("huobi.service.algo.get_open_orders.GetOpenOrdersService.request")
    def test_get_open_orders(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_open_orders()
        self.assertEqual(result, [])

    @mock.patch("huobi.service.algo.get_order_history.GetOrderHistoryService.request")
    def test_get_order_history(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_order_history("btcusdt", AlgoOrderStatus.CANCELED)
        self.assertEqual(result, [])

    @mock.patch("huobi.service.algo.get_order_by_cid.GetOrderByClientOrderIdService.request")
    def test_get_order(self, mock_request):
        mock_request.return_value = None
        result = self.client.get_order("c1")
        self.assertIsNone(result)


class TestSubuserClient(unittest.TestCase):
    def setUp(self):
        self.client = SubuserClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.subuser.post_create_subuser.PostSubuserCreationService.request")
    def test_post_create_subuser(self, mock_request):
        mock_request.return_value = []
        result = self.client.post_create_subuser([{"userName": "test"}])
        self.assertEqual(result, [])

    def test_post_create_subuser_none(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_create_subuser(None)

    @mock.patch("huobi.service.subuser.get_uid.GetUidService.request")
    def test_get_uid(self, mock_request):
        mock_request.return_value = 12345
        result = self.client.get_uid()
        self.assertEqual(result, 12345)


if __name__ == "__main__":
    unittest.main()
