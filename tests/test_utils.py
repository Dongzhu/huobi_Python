import unittest
from unittest import mock
import json
import time

from huobi.utils import *
from huobi.utils.api_signature import create_signature, utc_now
from huobi.utils.api_signature_v2 import create_signature_v2
from huobi.utils.url_params_builder import UrlParamsBuilder
from huobi.utils.json_parser import (default_parse, default_parse_list_dict, default_parse_fill_directly,
                                      default_parse_data_as_long, fill_obj, fill_obj_list, key_trans, safe_get)
from huobi.utils.input_checker import (check_symbol, check_symbol_list, check_currency, check_range,
                                        check_should_not_none, check_should_none, check_in_list, check_list,
                                        greater_or_equal, format_date, check_time_in_force,
                                        check_should_be_positive, check_should_not_empty)
from huobi.utils.time_service import (get_current_timestamp, convert_cst_in_millisecond_to_utc,
                                       convert_cst_in_second_to_utc, timestamp_to_date, date_to_timestamp,
                                       get_current_timestamp_in_second)
from huobi.utils.etf_result import etf_result_check
from huobi.exception.huobi_api_exception import HuobiApiException
from huobi.constant import *


class TestUrlParamsBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = UrlParamsBuilder()

    def test_put_url_with_string(self):
        self.builder.put_url("key", "value")
        self.assertEqual(self.builder.param_map["key"], "value")

    def test_put_url_with_none(self):
        self.builder.put_url("key", None)
        self.assertNotIn("key", self.builder.param_map)

    def test_put_url_with_int(self):
        self.builder.put_url("key", 123)
        self.assertEqual(self.builder.param_map["key"], "123")

    def test_put_url_with_list(self):
        lst = ["a", "b"]
        self.builder.put_url("key", lst)
        self.assertEqual(self.builder.param_map["key"], lst)

    def test_put_post(self):
        self.builder.put_post("key", "value")
        self.assertEqual(self.builder.post_map["key"], "value")

    def test_build_url_empty(self):
        self.assertEqual(self.builder.build_url(), "")

    def test_build_url_with_params(self):
        self.builder.put_url("a", "1")
        self.builder.put_url("b", "2")
        url = self.builder.build_url()
        self.assertTrue(url.startswith("?"))
        self.assertIn("a=1", url)
        self.assertIn("b=2", url)

    def test_build_url_to_json(self):
        self.builder.put_url("a", "1")
        result = json.loads(self.builder.build_url_to_json())
        self.assertEqual(result["a"], "1")


class TestApiSignature(unittest.TestCase):
    def test_create_signature_basic(self):
        builder = UrlParamsBuilder()
        with mock.patch("huobi.utils.api_signature.utc_now", return_value="2020-01-01T00:00:00"):
            create_signature("test_key", "test_secret", "GET", "https://api.huobi.pro/url", builder)
        self.assertEqual(builder.param_map["AccessKeyId"], "test_key")
        self.assertEqual(builder.param_map["SignatureVersion"], "2")
        self.assertEqual(builder.param_map["SignatureMethod"], "HmacSHA256")
        self.assertEqual(builder.param_map["Timestamp"], "2020-01-01T00:00:00")
        self.assertIn("Signature", builder.param_map)

    def test_create_signature_missing_key(self):
        builder = UrlParamsBuilder()
        with self.assertRaises(HuobiApiException) as ctx:
            create_signature(None, "secret", "GET", "https://api.huobi.pro/url", builder)
        self.assertEqual(ctx.exception.error_code, HuobiApiException.KEY_MISSING)

    def test_create_signature_missing_secret(self):
        builder = UrlParamsBuilder()
        with self.assertRaises(HuobiApiException) as ctx:
            create_signature("key", None, "GET", "https://api.huobi.pro/url", builder)
        self.assertEqual(ctx.exception.error_code, HuobiApiException.KEY_MISSING)

    def test_create_signature_empty_key(self):
        builder = UrlParamsBuilder()
        with self.assertRaises(HuobiApiException):
            create_signature("", "secret", "GET", "https://api.huobi.pro/url", builder)

    def test_create_signature_v2(self):
        builder = UrlParamsBuilder()
        with mock.patch("huobi.utils.api_signature_v2.utc_now", return_value="2020-01-01T00:00:00"):
            create_signature_v2("test_key", "test_secret", "GET", "wss://api.huobi.pro/ws/v2", builder)
        self.assertEqual(builder.param_map["accessKey"], "test_key")
        self.assertEqual(builder.param_map["signatureVersion"], "2.1")
        self.assertIn("signature", builder.param_map)
        self.assertEqual(builder.param_map["action"], "req")
        self.assertEqual(builder.param_map["ch"], "auth")

    def test_create_signature_v2_missing_key(self):
        builder = UrlParamsBuilder()
        with self.assertRaises(HuobiApiException):
            create_signature_v2(None, "secret", "GET", "wss://api.huobi.pro/ws/v2", builder)

    def test_utc_now_format(self):
        ts = utc_now()
        # Should match YYYY-MM-DDTHH:MM:SS format
        self.assertEqual(len(ts), 19)
        self.assertEqual(ts[10], "T")


class TestJsonParser(unittest.TestCase):
    def test_key_trans_with_hyphen(self):
        self.assertEqual(key_trans("filled-amount"), "filled_amount")

    def test_key_trans_short(self):
        self.assertEqual(key_trans("a"), "")

    def test_key_trans_none(self):
        self.assertEqual(key_trans(None), "")

    def test_fill_obj_basic(self):
        class TestObj:
            def __init__(self):
                self.name = ""
                self.age = 0
        data = {"name": "test", "age": 25}
        obj = fill_obj(data, TestObj)
        self.assertEqual(obj.name, "test")
        self.assertEqual(obj.age, 25)

    def test_fill_obj_none_data(self):
        class TestObj:
            pass
        obj = fill_obj(None, TestObj)
        self.assertIsInstance(obj, TestObj)

    def test_fill_obj_ignores_unknown_keys(self):
        class TestObj:
            def __init__(self):
                self.name = ""
        data = {"name": "test", "unknown": "value"}
        obj = fill_obj(data, TestObj)
        self.assertEqual(obj.name, "test")
        self.assertFalse(hasattr(obj, "unknown"))

    def test_fill_obj_list(self):
        class TestObj:
            def __init__(self):
                self.name = ""
        data = [{"name": "a"}, {"name": "b"}]
        result = fill_obj_list(data, TestObj)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "a")
        self.assertEqual(result[1].name, "b")

    def test_fill_obj_list_none(self):
        class TestObj:
            pass
        self.assertEqual(fill_obj_list(None, TestObj), [])

    def test_default_parse_list_dict_with_list(self):
        class Inner:
            def __init__(self):
                self.val = 0
        data = [{"val": 1}, {"val": 2}]
        result = default_parse_list_dict(data, Inner, [])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].val, 1)

    def test_default_parse_list_dict_empty(self):
        class Inner:
            pass
        self.assertIsNone(default_parse_list_dict([], Inner, None))

    def test_default_parse_list_dict_default(self):
        class Inner:
            pass
        self.assertEqual(default_parse_list_dict(None, Inner, "default"), "default")

    def test_default_parse_data_as_long_with_key(self):
        data = {"data": {"order_id": 12345}}
        self.assertEqual(default_parse_data_as_long(data, "order_id"), 12345)

    def test_default_parse_data_as_long_no_key(self):
        data = {"data": 67890}
        self.assertEqual(default_parse_data_as_long(data), 67890)

    def test_default_parse_data_as_long_none_data(self):
        self.assertEqual(default_parse_data_as_long(None, "key", 0), 0)

    def test_default_parse_data_as_long_none_value(self):
        data = {"data": {"key": None}}
        self.assertEqual(default_parse_data_as_long(data, "key", 42), 42)

    def test_default_parse_fill_directly(self):
        class TestObj:
            def __init__(self):
                self.name = ""
                self.age = 0
        data = {"name": "test", "age": 30}
        obj = default_parse_fill_directly(data, TestObj)
        self.assertEqual(obj.name, "test")
        self.assertEqual(obj.age, 30)

    def test_default_parse_none(self):
        class TestObj:
            pass
        obj = default_parse(None, TestObj)
        self.assertIsInstance(obj, TestObj)

    def test_safe_get_with_key(self):
        data = {"key": "value"}
        self.assertEqual(safe_get(data, "key"), "value")

    def test_safe_get_missing_key(self):
        data = {"key": "value"}
        self.assertIsNone(safe_get(data, "missing"))

    def test_safe_get_default(self):
        data = {"key": "value"}
        self.assertEqual(safe_get(data, "missing", "default"), "default")

    def test_safe_get_none_dict(self):
        self.assertEqual(safe_get(None, "key", "default"), "default")


class TestInputChecker(unittest.TestCase):
    def test_check_symbol_valid(self):
        check_symbol("btcusdt")  # Should not raise

    def test_check_symbol_not_string(self):
        with self.assertRaises(HuobiApiException):
            check_symbol(123)

    def test_check_symbol_empty(self):
        with self.assertRaises(HuobiApiException):
            check_symbol("")

    def test_check_symbol_invalid(self):
        with self.assertRaises(HuobiApiException):
            check_symbol("btc usdt")

    def test_check_symbol_list_valid(self):
        check_symbol_list(["btcusdt", "ethusdt"])  # Should not raise

    def test_check_symbol_list_not_list(self):
        with self.assertRaises(HuobiApiException):
            check_symbol_list("btcusdt")

    def test_check_symbol_list_empty(self):
        with self.assertRaises(HuobiApiException):
            check_symbol_list([])

    def test_check_currency_valid(self):
        check_currency("btc")  # Should not raise

    def test_check_currency_not_string(self):
        with self.assertRaises(HuobiApiException):
            check_currency(123)

    def test_check_range_valid(self):
        check_range(5, 1, 10, "test")  # Should not raise

    def test_check_range_none(self):
        check_range(None, 1, 10, "test")  # Should not raise

    def test_check_range_too_high(self):
        with self.assertRaises(HuobiApiException):
            check_range(15, 1, 10, "test")

    def test_check_range_too_low(self):
        with self.assertRaises(HuobiApiException):
            check_range(0, 1, 10, "test")

    def test_check_should_not_none(self):
        with self.assertRaises(HuobiApiException):
            check_should_not_none(None, "test")
        check_should_not_none("value", "test")  # Should not raise

    def test_check_should_none(self):
        with self.assertRaises(HuobiApiException):
            check_should_none("value", "test")
        check_should_none(None, "test")  # Should not raise

    def test_check_in_list_valid(self):
        check_in_list("a", ["a", "b", "c"], "test")  # Should not raise

    def test_check_in_list_invalid(self):
        with self.assertRaises(HuobiApiException):
            check_in_list("d", ["a", "b", "c"], "test")

    def test_check_in_list_none(self):
        check_in_list(None, ["a", "b"], "test")  # Should not raise

    def test_check_list_valid(self):
        check_list([1, 2, 3], 1, 5, "test")  # Should not raise

    def test_check_list_too_long(self):
        with self.assertRaises(HuobiApiException):
            check_list([1, 2, 3, 4, 5, 6], 1, 5, "test")

    def test_check_list_too_short(self):
        with self.assertRaises(HuobiApiException):
            check_list([], 1, 5, "test")

    def test_greater_or_equal(self):
        greater_or_equal(5, 5, "test")  # Should not raise
        with self.assertRaises(HuobiApiException):
            greater_or_equal(3, 5, "test")

    def test_format_date_valid(self):
        result = format_date("2020-01-15", "test")
        self.assertEqual(result, "2020-01-15")

    def test_format_date_none(self):
        self.assertIsNone(format_date(None, "test"))

    def test_format_date_invalid(self):
        with self.assertRaises(HuobiApiException):
            format_date("invalid", "test")

    def test_format_date_not_string(self):
        with self.assertRaises(HuobiApiException):
            format_date(123, "test")

    def test_check_time_in_force_none(self):
        check_time_in_force(None, OrderType.BUY_LIMIT)  # Should not raise

    def test_check_time_in_force_market_with_gtc(self):
        with self.assertRaises(HuobiApiException):
            check_time_in_force(TimeInForceType.GTC, OrderType.BUY_MARKET)

    def test_check_time_in_force_limit_with_gtc(self):
        check_time_in_force(TimeInForceType.GTC, OrderType.BUY_LIMIT)  # Should not raise

    def test_check_time_in_force_algo_market(self):
        with self.assertRaises(HuobiApiException):
            check_time_in_force(TimeInForceType.FOK, AlgoOrderType.MARKET)

    def test_check_should_be_positive(self):
        check_should_be_positive(5, "test")  # Should not raise
        with self.assertRaises(HuobiApiException):
            check_should_be_positive(0, "test")
        with self.assertRaises(HuobiApiException):
            check_should_be_positive(-1, "test")

    def test_check_should_not_empty(self):
        check_should_not_empty("value", "test")  # Should not raise
        check_should_not_empty([1], "test")  # Should not raise
        with self.assertRaises(HuobiApiException):
            check_should_not_empty("", "test")
        with self.assertRaises(HuobiApiException):
            check_should_not_empty([], "test")


class TestTimeService(unittest.TestCase):
    def test_get_current_timestamp(self):
        ts = get_current_timestamp()
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)
        # Should be in milliseconds (13 digits)
        self.assertGreater(ts, 1000000000000)

    def test_get_current_timestamp_in_second(self):
        ts = get_current_timestamp_in_second()
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)

    def test_convert_cst_in_second_to_utc_valid(self):
        # 2020-01-01 00:00:00 UTC in seconds
        result = convert_cst_in_second_to_utc(1577836800)
        self.assertEqual(result, (1577836800 - 8 * 3600) * 1000)

    def test_convert_cst_in_second_to_utc_out_of_range(self):
        self.assertEqual(convert_cst_in_second_to_utc(0), 0)

    def test_convert_cst_in_second_to_utc_none(self):
        self.assertEqual(convert_cst_in_second_to_utc(None), 0)

    def test_convert_cst_in_millisecond_to_utc_valid(self):
        result = convert_cst_in_millisecond_to_utc(1577836800000)
        self.assertEqual(result, 1577836800000 - 8 * 3600 * 1000)

    def test_convert_cst_in_millisecond_to_utc_none(self):
        self.assertEqual(convert_cst_in_millisecond_to_utc(None), 0)

    def test_timestamp_to_date(self):
        # 2020-01-01 00:00:00 UTC in ms
        result = timestamp_to_date(1577836800000)
        self.assertEqual(result, "2020-01-01 00:00:00")

    def test_timestamp_to_date_none(self):
        self.assertEqual(timestamp_to_date(None), "")

    def test_date_to_timestamp(self):
        ts = date_to_timestamp("2020-01-01")
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)

    def test_date_to_timestamp_none(self):
        self.assertEqual(date_to_timestamp(None), 0)


class TestEtfResult(unittest.TestCase):
    def test_etf_result_check_200(self):
        self.assertEqual(etf_result_check(200), "")

    def test_etf_result_check_10400(self):
        self.assertEqual(etf_result_check(10400), "Invalid ETF name")

    def test_etf_result_check_13403(self):
        self.assertEqual(etf_result_check(13403), "Insufficient asset to create ETF")

    def test_etf_result_check_13500(self):
        self.assertEqual(etf_result_check(13500), "System error")

    def test_etf_result_check_none(self):
        self.assertEqual(etf_result_check(None), "")

    def test_etf_result_check_string(self):
        self.assertEqual(etf_result_check("200"), "")

    def test_etf_result_check_unknown(self):
        self.assertEqual(etf_result_check(99999), "")


class TestChannels(unittest.TestCase):
    def test_kline_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(kline_channel("btcusdt", "1min"))
        self.assertEqual(result["sub"], "market.btcusdt.kline.1min")
        self.assertEqual(result["id"], "12345")

    def test_trade_detail_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(trade_detail_channel("btcusdt"))
        self.assertEqual(result["sub"], "market.btcusdt.trade.detail")

    def test_price_depth_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(price_depth_channel("btcusdt", DepthStep.STEP0))
        self.assertEqual(result["sub"], "market.btcusdt.depth.step0")

    def test_price_depth_bbo_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(price_depth_bbo_channel("btcusdt"))
        self.assertEqual(result["sub"], "market.btcusdt.bbo")

    def test_orders_update_channel(self):
        result = json.loads(orders_update_channel("btcusdt"))
        self.assertEqual(result["action"], "sub")
        self.assertEqual(result["ch"], "orders#btcusdt")

    def test_market_detail_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(market_detail_channel("btcusdt"))
        self.assertEqual(result["sub"], "market.btcusdt.detail")

    def test_accounts_update_channel(self):
        result = json.loads(accounts_update_channel(1))
        self.assertEqual(result["action"], "sub")
        self.assertEqual(result["ch"], "accounts.update#1")

    def test_mbp_increase_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(mbp_increase_channel("btcusdt", 150))
        self.assertEqual(result["sub"], "market.btcusdt.mbp.150")

    def test_mbp_full_channel(self):
        with mock.patch("huobi.utils.channels.get_current_timestamp", return_value=12345):
            result = json.loads(mbp_full_channel("btcusdt", 20))
        self.assertEqual(result["sub"], "market.btcusdt.mbp.refresh.20")

    def test_trade_clearing_channel(self):
        result = json.loads(trade_clearing_channel("btcusdt"))
        self.assertEqual(result["action"], "sub")
        self.assertEqual(result["ch"], "trade.clearing#btcusdt")

    def test_trade_clearing_channel_all(self):
        result = json.loads(trade_clearing_channel("*"))
        self.assertEqual(result["ch"], "trade.clearing#*")


class TestChannelsRequest(unittest.TestCase):
    def test_request_kline_channel(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_kline_channel("btcusdt", "1min"))
        self.assertEqual(result["req"], "market.btcusdt.kline.1min")

    def test_request_kline_channel_with_range(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_kline_channel("btcusdt", "1min", 1000, 2000))
        self.assertEqual(result["from"], 1000)
        self.assertEqual(result["to"], 2000)

    def test_request_trade_detail_channel(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_trade_detail_channel("btcusdt"))
        self.assertEqual(result["req"], "market.btcusdt.trade.detail")

    def test_request_price_depth_channel(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_price_depth_channel("btcusdt", "step0"))
        self.assertEqual(result["req"], "market.btcusdt.depth.step0")

    def test_request_market_detail_channel(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_market_detail_channel("btcusdt"))
        self.assertEqual(result["req"], "market.btcusdt.detail")

    def test_request_account_list_channel(self):
        result = json.loads(request_account_list_channel("req123"))
        self.assertEqual(result["op"], "req")
        self.assertEqual(result["topic"], "accounts.list")
        self.assertEqual(result["cid"], "req123")

    def test_request_order_list_channel(self):
        with mock.patch("huobi.utils.channels_request.get_current_timestamp", return_value=12345):
            result = json.loads(request_order_list_channel("btcusdt", 123, "submitted", "req456"))
        self.assertEqual(result["op"], "req")
        self.assertEqual(result["topic"], "orders.list")
        self.assertEqual(result["symbol"], "btcusdt")
        self.assertEqual(result["account-id"], 123)

    def test_request_order_detail_channel(self):
        result = json.loads(request_order_detail_channel(789, "req789"))
        self.assertEqual(result["op"], "req")
        self.assertEqual(result["topic"], "orders.detail")
        self.assertEqual(result["order-id"], "789")


if __name__ == "__main__":
    unittest.main()
