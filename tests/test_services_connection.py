import unittest
from unittest import mock
import json
from huobi.connection.impl.restapi_invoker import call_sync, check_response, call_sync_perforence_test
from huobi.connection.impl.restapi_request import RestApiRequest
from huobi.connection.restapi_sync_client import RestApiSyncClient
from huobi.connection.impl.websocket_manage import WebsocketManage, ConnectionState
from huobi.connection.impl.websocket_watchdog import WebSocketWatchDog
from huobi.exception.huobi_api_exception import HuobiApiException
from huobi.constant import *


class TestCheckResponse(unittest.TestCase):
    def test_check_response_ok(self):
        data = {"status": "ok", "data": "result"}
        # Should not raise
        check_response(data)

    def test_check_response_error(self):
        data = {"status": "error", "err-code": "err_code", "err-msg": "error message"}
        with self.assertRaises(HuobiApiException) as ctx:
            check_response(data)
        self.assertEqual(ctx.exception.error_code, HuobiApiException.EXEC_ERROR)
        self.assertIn("err_code", ctx.exception.error_message)

    def test_check_response_error_with_code(self):
        data = {"code": 10001, "message": "error message"}
        with self.assertRaises(HuobiApiException) as ctx:
            check_response(data)
        self.assertIn("10001", ctx.exception.error_message)

    def test_check_response_not_success(self):
        data = {"success": False, "code": 20001, "message": "not success"}
        with self.assertRaises(HuobiApiException) as ctx:
            check_response(data)
        self.assertIn("20001", ctx.exception.error_message)

    def test_check_response_none(self):
        with self.assertRaises(HuobiApiException):
            check_response(None)

    def test_check_response_missing_status(self):
        data = {"data": "result"}
        with self.assertRaises(HuobiApiException):
            check_response(data)


class TestRestApiRequest(unittest.TestCase):
    def test_get_request_no_auth(self):
        from huobi.utils.url_params_builder import UrlParamsBuilder
        builder = UrlParamsBuilder()
        builder.put_url("symbol", "btcusdt")
        request = RestApiRequest()
        request.method = "GET"
        request.host = "https://api.huobi.pro"
        request.url = "/market/detail" + builder.build_url()
        request.json_parser = lambda x: x
        self.assertIn("symbol=btcusdt", request.url)

    def test_post_request(self):
        from huobi.utils.url_params_builder import UrlParamsBuilder
        builder = UrlParamsBuilder()
        builder.put_post("account-id", 123)
        request = RestApiRequest()
        request.method = "POST"
        request.host = "https://api.huobi.pro"
        request.url = "/v1/order/orders"
        request.post_body = builder.post_map
        request.json_parser = lambda x: x
        self.assertIsNotNone(request.post_body)


class TestCallSync(unittest.TestCase):
    def _make_request(self, method, url, params=None, parse=None):
        from huobi.utils.url_params_builder import UrlParamsBuilder
        builder = UrlParamsBuilder()
        if params:
            if method == "GET":
                for k, v in params.items():
                    builder.put_url(k, v)
            else:
                for k, v in params.items():
                    builder.put_post(k, v)
        request = RestApiRequest()
        request.method = method
        request.host = "https://api.huobi.pro"
        request.url = url + builder.build_url()
        if method == "POST":
            request.post_body = builder.post_map
        request.json_parser = parse or (lambda x: x.get("data"))
        return request

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_call_sync_get(self, mock_get):
        mock_response = mock.Mock()
        mock_response.text = json.dumps({"status": "ok", "data": "result"})
        mock_get.return_value = mock_response

        request = self._make_request("GET", "/market/detail", {"symbol": "btcusdt"})
        result = call_sync(request)
        self.assertEqual(result, "result")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_call_sync_get_checked(self, mock_get):
        mock_response = mock.Mock()
        mock_response.text = "plain text"
        mock_get.return_value = mock_response

        request = self._make_request("GET", "/test")
        result = call_sync(request, is_checked=True)
        self.assertEqual(result, "plain text")

    @mock.patch("huobi.connection.impl.restapi_invoker.session.post")
    def test_call_sync_post(self, mock_post):
        mock_response = mock.Mock()
        mock_response.text = json.dumps({"status": "ok", "data": 123})
        mock_post.return_value = mock_response

        request = self._make_request("POST", "/test", {"test": "value"})
        result = call_sync(request)
        self.assertEqual(result, 123)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_call_sync_error_response(self, mock_get):
        mock_response = mock.Mock()
        mock_response.text = json.dumps({"status": "error", "err-code": "err", "err-msg": "msg"})
        mock_get.return_value = mock_response

        request = self._make_request("GET", "/test")
        with self.assertRaises(HuobiApiException):
            call_sync(request)

    @mock.patch("huobi.connection.impl.restapi_invoker.session.get")
    def test_call_sync_performance_test(self, mock_get):
        mock_response = mock.Mock()
        mock_response.text = json.dumps({"status": "ok", "data": "result"})
        mock_response.elapsed = mock.Mock()
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response

        request = self._make_request("GET", "/test")
        result = call_sync_perforence_test(request)
        self.assertEqual(result[0], "result")
        self.assertEqual(result[1], 0.1)
        self.assertIsInstance(result[2], float)


class TestRestApiSyncClient(unittest.TestCase):
    @mock.patch("huobi.connection.restapi_sync_client.call_sync")
    def test_request_process(self, mock_call_sync):
        mock_call_sync.return_value = "result"

        client = RestApiSyncClient(url="https://api.huobi.pro", api_key="key", secret_key="secret")
        result = client.request_process("GET", "/test", {"param": "value"}, lambda x: x)
        self.assertEqual(result, "result")

    @mock.patch("huobi.connection.restapi_sync_client.call_sync")
    def test_request_process_with_signature(self, mock_call_sync):
        mock_call_sync.return_value = "result"

        client = RestApiSyncClient(url="https://api.huobi.pro", api_key="key", secret_key="secret")
        result = client.request_process("GET_SIGN", "/test", {"param": "value"}, lambda x: x)
        self.assertEqual(result, "result")

    def test_request_process_invalid_method(self):
        client = RestApiSyncClient(url="https://api.huobi.pro", api_key="key", secret_key="secret")
        with self.assertRaises(HuobiApiException):
            client.request_process("INVALID", "/test", {}, lambda x: x)

    @mock.patch("huobi.connection.restapi_sync_client.call_sync")
    def test_request_process_post_batch(self, mock_call_sync):
        mock_call_sync.return_value = [1, 2]
        client = RestApiSyncClient(url="https://api.huobi.pro", api_key="key", secret_key="secret")
        result = client.request_process_post_batch("POST", "/test", [{"a": 1}], lambda x: x)
        self.assertEqual(result, [1, 2])

    def test_init_with_log(self):
        client = RestApiSyncClient(url="https://api.huobi.pro", init_log=True)
        self.assertIsNotNone(client)


class TestWebsocketManage(unittest.TestCase):
    def _make_request(self):
        req = mock.Mock()
        req.api_version = "v1"
        req.is_trading = False
        req.is_mbp_feed = False
        req.subscription_handler = None
        return req

    def test_init(self):
        req = self._make_request()
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        self.assertEqual(manage.state, ConnectionState.IDLE)
        self.assertEqual(manage.original_connection, None)

    def test_on_open(self):
        req = self._make_request()
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        manage.original_connection = mock.Mock()
        manage.on_open(manage.original_connection)
        self.assertEqual(manage.state, ConnectionState.CONNECTED)

    def test_on_close(self):
        from huobi.connection.impl.websocket_manage import websocket_connection_handler
        req = self._make_request()
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        manage.original_connection = mock.Mock()
        websocket_connection_handler[manage.original_connection] = manage
        manage.close()
        self.assertEqual(manage.state, ConnectionState.CLOSED)

    @mock.patch("huobi.connection.impl.websocket_manage.get_current_timestamp", return_value=1000)
    def test_close_and_wait_reconnect(self, mock_ts):
        req = self._make_request()
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        manage.original_connection = mock.Mock()
        manage.close_and_wait_reconnect(5000)
        self.assertEqual(manage.state, ConnectionState.WAIT_RECONNECT)
        self.assertEqual(manage.reconnect_at, 6000)

    def test_connect_creates_thread(self):
        req = self._make_request()
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        with mock.patch("threading.Thread.start") as mock_start:
            manage.connect()
            mock_start.assert_called_once()


class TestWebSocketWatchDog(unittest.TestCase):
    def setUp(self):
        WebSocketWatchDog.websocket_manage_list = list()

    @mock.patch.object(WebSocketWatchDog, "start")
    def test_init(self, mock_start):
        dog = WebSocketWatchDog(60)
        self.assertIsNotNone(dog)

    @mock.patch.object(WebSocketWatchDog, "start")
    def test_add_connection(self, mock_start):
        dog = WebSocketWatchDog(60)
        req = mock.Mock()
        req.api_version = "v1"
        req.is_trading = False
        req.is_mbp_feed = False
        req.subscription_handler = None
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        dog.on_connection_created(manage)
        self.assertEqual(len(dog.websocket_manage_list), 1)

    @mock.patch.object(WebSocketWatchDog, "start")
    def test_remove_connection(self, mock_start):
        dog = WebSocketWatchDog(60)
        req = mock.Mock()
        req.api_version = "v1"
        req.is_trading = False
        req.is_mbp_feed = False
        req.subscription_handler = None
        manage = WebsocketManage("key", "secret", "wss://api.huobi.pro/ws", req)
        dog.on_connection_created(manage)
        dog.on_connection_closed(manage)
        self.assertEqual(len(dog.websocket_manage_list), 0)


class TestConstants(unittest.TestCase):
    def test_account_change_type(self):
        self.assertEqual(AccountChangeType.ORDER_PLACE, "order-place")
        self.assertEqual(AccountChangeType.ORDER_MATCH, "order-match")
        self.assertEqual(AccountChangeType.ORDER_REFUND, "order-refund")
        self.assertEqual(AccountChangeType.ORDER_CANCEL, "order-cancel")
        self.assertEqual(AccountChangeType.ORDER_FEE_REFUND, "order-fee-refund")
        self.assertEqual(AccountChangeType.MARGIN_TRANSFER, "margin-transfer")
        self.assertEqual(AccountChangeType.MARGIN_LOAN, "margin-loan")
        self.assertEqual(AccountChangeType.MARGIN_INTEREST, "margin-interest")
        self.assertEqual(AccountChangeType.MARGIN_REPAY, "margin-repay")
        self.assertEqual(AccountChangeType.OTHER, "other")
        self.assertEqual(AccountChangeType.DEPOSIT, "deposit")
        self.assertEqual(AccountChangeType.WITHDRAW, "withdraw")
        self.assertIsNone(AccountChangeType.INVALID)

    def test_wallet_reject_typo_fixed(self):
        # Verify WALEETREJECT typo is fixed to WALLETREJECT
        self.assertEqual(WithdrawState.WALLETREJECT, "wallet-reject")
        # Ensure old typo no longer exists
        self.assertFalse(hasattr(WithdrawState, "WALEETREJECT"))

    def test_order_type(self):
        self.assertEqual(OrderType.SELL_MARKET, "sell-market")
        self.assertEqual(OrderType.BUY_MARKET, "buy-market")
        self.assertEqual(OrderType.SELL_LIMIT, "sell-limit")
        self.assertEqual(OrderType.BUY_LIMIT, "buy-limit")

    def test_account_type(self):
        self.assertEqual(AccountType.SPOT, "spot")
        self.assertEqual(AccountType.MARGIN, "margin")
        self.assertEqual(AccountType.SUPER_MARGIN, "super-margin")

    def test_candlestick_interval(self):
        self.assertEqual(CandlestickInterval.MIN1, "1min")
        self.assertEqual(CandlestickInterval.MIN5, "5min")
        self.assertEqual(CandlestickInterval.DAY1, "1day")

    def test_depth_step(self):
        self.assertEqual(DepthStep.STEP0, "step0")
        self.assertEqual(DepthStep.STEP5, "step5")

    def test_order_state(self):
        self.assertEqual(OrderState.SUBMITTED, "submitted")
        self.assertEqual(OrderState.FILLED, "filled")
        self.assertEqual(OrderState.CANCELED, "canceled")

    def test_algo_order_type(self):
        self.assertEqual(AlgoOrderType.LIMIT, "limit")
        self.assertEqual(AlgoOrderType.MARKET, "market")

    def test_time_in_force_type(self):
        self.assertEqual(TimeInForceType.GTC, "gtc")
        self.assertEqual(TimeInForceType.BOC, "boc")
        self.assertEqual(TimeInForceType.FOK, "fok")
        self.assertEqual(TimeInForceType.IOC, "ioc")


class TestException(unittest.TestCase):
    def test_exception_with_code(self):
        exc = HuobiApiException("code", "message")
        self.assertEqual(exc.error_code, "code")
        self.assertEqual(exc.error_message, "message")
        self.assertIn("code", str(exc))

    def test_exception_without_code(self):
        exc = HuobiApiException(None, "message")
        self.assertIsNone(exc.error_code)
        self.assertEqual(exc.error_message, "message")

    def test_exception_constants(self):
        self.assertEqual(HuobiApiException.EXEC_ERROR, "ExecuteError")
        self.assertEqual(HuobiApiException.INPUT_ERROR, "InputError")
        self.assertEqual(HuobiApiException.SYS_ERROR, "SysError")
        self.assertEqual(HuobiApiException.KEY_MISSING, "KeyMissing")
        self.assertEqual(HuobiApiException.RUNTIME_ERROR, "RuntimeError")


if __name__ == "__main__":
    unittest.main()
