import unittest
from unittest import mock
import sys
import io
from huobi.utils.print_mix_object import *
from huobi.utils.log_info import LogInfo, LogLevel
from huobi.utils.input_checker import *
from huobi.utils.json_parser import *
from huobi.utils.time_service import *
from huobi.utils.etf_result import etf_result_check
from huobi.constant import *
from huobi.exception.huobi_api_exception import HuobiApiException


class TestPrintMixObject(unittest.TestCase):
    def test_type_check_is_basic(self):
        self.assertTrue(TypeCheck.is_basic("string"))
        self.assertTrue(TypeCheck.is_basic(123))
        self.assertTrue(TypeCheck.is_basic(1.5))
        self.assertFalse(TypeCheck.is_basic([1, 2]))
        self.assertFalse(TypeCheck.is_basic({"a": 1}))
        self.assertFalse(TypeCheck.is_basic(None))

    def test_type_check_is_list(self):
        self.assertTrue(TypeCheck.is_list([1, 2]))
        self.assertFalse(TypeCheck.is_list("string"))
        self.assertFalse(TypeCheck.is_list({"a": 1}))

    def test_type_check_is_dict(self):
        self.assertTrue(TypeCheck.is_dict({"a": 1}))
        self.assertFalse(TypeCheck.is_dict([1, 2]))
        self.assertFalse(TypeCheck.is_dict("string"))

    def test_print_basic(self):
        PrintMix.print_data(None)
        PrintMix.print_data("string")
        PrintMix.print_data(123)
        PrintMix.print_data(1.5)
        PrintMix.print_data(True)

    def test_print_list(self):
        PrintMix.print_data([1, 2, 3])
        PrintMix.print_data([])

    def test_print_dict(self):
        PrintMix.print_data({"key": "value"})
        PrintMix.print_data({})

    def test_print_object(self):
        class TestObj:
            def __init__(self):
                self.name = "test"
                self.value = 123
        obj = TestObj()
        PrintMix.print_data(obj)


class TestLogInfo(unittest.TestCase):
    def test_log_output(self):
        captured = io.StringIO()
        sys.stdout = captured
        LogInfo.output("test message", LogLevel.DEBUG)
        sys.stdout = sys.__stdout__
        self.assertIn("test message", captured.getvalue())

    def test_log_output_list(self):
        class TestObj:
            def print_object(self):
                print("test object")
        captured = io.StringIO()
        sys.stdout = captured
        LogInfo.output_list([TestObj()], LogLevel.DEBUG)
        sys.stdout = sys.__stdout__
        self.assertIn("test object", captured.getvalue())


class TestInputCheckerEdgeCases(unittest.TestCase):
    def test_check_symbol_list_with_invalid_symbol(self):
        with self.assertRaises(HuobiApiException):
            check_symbol_list(["btc usdt", "ethusdt"])

    def test_check_currency_invalid(self):
        with self.assertRaises(HuobiApiException):
            check_currency("btc usdt")

    def test_check_range_equal_bounds(self):
        check_range(5, 5, 5, "test")

    def test_check_in_list_with_none_value(self):
        check_in_list(None, ["a", "b"], "test")

    def test_check_list_none(self):
        check_list(None, 1, 5, "test")

    def test_check_list_not_list(self):
        with self.assertRaises(HuobiApiException):
            check_list("not a list", 1, 5, "test")

    def test_greater_or_equal_none(self):
        greater_or_equal(None, 5, "test")

    def test_check_should_be_positive_none(self):
        check_should_be_positive(None, "test")

    def test_check_should_be_positive_zero(self):
        with self.assertRaises(HuobiApiException):
            check_should_be_positive(0, "test")

    def test_check_should_not_empty_none(self):
        with self.assertRaises(HuobiApiException):
            check_should_not_empty(None, "test")

    def test_check_should_not_empty_dict(self):
        check_should_not_empty({"a": 1}, "test")
        with self.assertRaises(HuobiApiException):
            check_should_not_empty({}, "test")


class TestJsonParserEdgeCases(unittest.TestCase):
    def test_key_trans_long_string(self):
        self.assertEqual(key_trans("a-b-c"), "a_b_c")

    def test_fill_obj_with_nested(self):
        class Inner:
            def __init__(self):
                self.val = 0
        class Outer:
            def __init__(self):
                self.inner = None
        data = {"inner": {"val": 42}}
        obj = fill_obj(data, Outer)
        self.assertIsInstance(obj.inner, dict)

    def test_fill_obj_list_with_none_items(self):
        class TestObj:
            def __init__(self):
                self.val = 0
        data = [{"val": 1}, None, {"val": 3}]
        result = fill_obj_list(data, TestObj)
        self.assertEqual(len(result), 2)

    def test_default_parse_with_inner_list(self):
        class Inner:
            def __init__(self):
                self.val = 0
        class Outer:
            def __init__(self):
                self.items = None
        data = {"items": [{"val": 1}, {"val": 2}]}
        obj = default_parse(data, Outer, Inner)
        self.assertEqual(len(obj.items), 2)

    def test_default_parse_with_inner_dict(self):
        class Inner:
            def __init__(self):
                self.val = 0
        class Outer:
            def __init__(self):
                self.info = None
        data = {"info": {"val": 42}}
        obj = default_parse(data, Outer, Inner)
        self.assertEqual(obj.info.val, 42)

    def test_default_parse_data_as_long_string(self):
        data = {"data": "12345"}
        self.assertEqual(default_parse_data_as_long(data), 12345)

    def test_default_parse_data_as_long_invalid(self):
        data = {"data": "invalid"}
        self.assertEqual(default_parse_data_as_long(data, None, 0), 0)

    def test_default_parse_list_dict_with_dict(self):
        class Inner:
            def __init__(self):
                self.val = 0
        data = {"val": 42}
        result = default_parse_list_dict(data, Inner, None)
        self.assertEqual(result.val, 42)

    def test_default_parse_fill_directly_none(self):
        class TestObj:
            pass
        obj = default_parse_fill_directly(None, TestObj)
        self.assertIsInstance(obj, TestObj)

    def test_safe_get_with_default(self):
        self.assertEqual(safe_get({}, "key", "default"), "default")


class TestTimeServiceEdgeCases(unittest.TestCase):
    def test_convert_cst_in_second_to_utc_invalid_string(self):
        self.assertEqual(convert_cst_in_second_to_utc("invalid"), 0)

    def test_convert_cst_in_millisecond_to_utc_invalid_string(self):
        self.assertEqual(convert_cst_in_millisecond_to_utc("invalid"), 0)

    def test_timestamp_to_date_invalid(self):
        self.assertEqual(timestamp_to_date("invalid"), "")

    def test_date_to_timestamp_invalid(self):
        self.assertEqual(date_to_timestamp("invalid"), 0)

    def test_get_current_timestamp_in_second(self):
        ts = get_current_timestamp_in_second()
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)


class TestEtfResultEdgeCases(unittest.TestCase):
    def test_etf_result_check_13404(self):
        self.assertEqual(etf_result_check(13404), "Create and redemption disabled due to system setup")

    def test_etf_result_check_13405(self):
        self.assertEqual(etf_result_check(13405), "Create and redemption disabled due to configuration issue")

    def test_etf_result_check_13406(self):
        self.assertEqual(etf_result_check(13406), "Invalid API call")

    def test_etf_result_check_13410(self):
        self.assertEqual(etf_result_check(13410), "API authentication fails")

    def test_etf_result_check_13601(self):
        self.assertEqual(etf_result_check(13601), "Create and redemption disabled during rebalance")

    def test_etf_result_check_13603(self):
        self.assertEqual(etf_result_check(13603), "Create and redemption disabled due to other reason")

    def test_etf_result_check_13604(self):
        self.assertEqual(etf_result_check(13604), "Create suspended")

    def test_etf_result_check_13605(self):
        self.assertEqual(etf_result_check(13605), "Redemption suspended")

    def test_etf_result_check_13606(self):
        self.assertIn("Amount incorrect", etf_result_check(13606))


class TestCrossMarginClient(unittest.TestCase):
    def setUp(self):
        from huobi.client.margin import MarginClient
        self.client = MarginClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.margin.get_cross_margin_loan_info.GetCrossMarginLoanInfoService.request")
    def test_get_loan_info(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_cross_margin_loan_info()
        self.assertEqual(result, [])

    @mock.patch("huobi.service.margin.get_cross_margin_account_balance.GetCrossMarginAccountBalanceService.request")
    def test_get_cross_margin_account_balance(self, mock_request):
        mock_request.return_value = []
        result = self.client.get_cross_margin_account_balance()
        self.assertEqual(result, [])

    @mock.patch("huobi.service.margin.post_cross_margin_transfer_in.PostCrossMarginTransferInService.request")
    def test_transfer_in(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_cross_margin_transfer_in("btc", 1.0)
        self.assertEqual(result, 123)

    def test_transfer_in_none_currency(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_cross_margin_transfer_in(None, 1.0)


class TestCrossMarginLoan(unittest.TestCase):
    def setUp(self):
        from huobi.client.margin import MarginClient
        self.client = MarginClient(api_key="test", secret_key="test")

    @mock.patch("huobi.service.margin.post_cross_margin_create_loan_orders.PostCrossMarginCreateLoanOrdersService.request")
    def test_apply_loan(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_cross_margin_create_loan_orders("btc", 1.0)
        self.assertEqual(result, 123)

    def test_apply_loan_none_currency(self):
        with self.assertRaises(HuobiApiException):
            self.client.post_cross_margin_create_loan_orders(None, 1.0)

    @mock.patch("huobi.service.margin.post_cross_margin_loan_order_repay.PostCrossMarginLoanOrderRepayService.request")
    def test_repay_loan(self, mock_request):
        mock_request.return_value = 123
        result = self.client.post_cross_margin_loan_order_repay("123", 1.0)
        self.assertEqual(result, 123)


class TestSystem(unittest.TestCase):
    def test_http_method_constants(self):
        from huobi.constant.system import HttpMethod
        self.assertEqual(HttpMethod.GET, "GET")
        self.assertEqual(HttpMethod.POST, "POST")
        self.assertEqual(HttpMethod.GET_SIGN, "GET_SIGN")
        self.assertEqual(HttpMethod.POST_SIGN, "POST_SIGN")

    def test_api_version_constants(self):
        from huobi.constant.system import ApiVersion
        self.assertEqual(ApiVersion.VERSION_V1, "v1")
        self.assertEqual(ApiVersion.VERSION_V2, "v2")

    def test_get_default_server_url(self):
        from huobi.constant.system import get_default_server_url
        url = get_default_server_url(None)
        self.assertIn("huobi", url)


if __name__ == "__main__":
    unittest.main()
