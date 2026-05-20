import pytest
import os
import tempfile
from common.report_comparator import ReportComparator

pytestmark = pytest.mark.api

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "reports")


def test_compare_trading_reports():
    """测试对比交易报表"""
    comp = ReportComparator()
    expected = os.path.join(DATA_DIR, "expected.csv")
    actual = os.path.join(DATA_DIR, "actual.csv")

    result = comp.compare_csv(expected, actual)

    # 预期有差异：第二行价格不同，第五行是新增
    assert result["is_equal"] is False
    assert result["diff_count"] == 2


def test_generate_trading_diff_report():
    """测试生成交易报表差异报告"""
    comp = ReportComparator()
    expected = os.path.join(DATA_DIR, "expected.csv")
    actual = os.path.join(DATA_DIR, "actual.csv")

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        output = f.name

    try:
        comp.generate_diff_report(expected, actual, output)
        assert os.path.exists(output)

        with open(output, "r", encoding="utf-8") as f:
            content = f.read()

        assert "报表对比报告" in content
        assert "5.20" in content  # 原始价格
        assert "5.25" in content  # 修改后价格
        assert "600050" in content  # 新增行
    finally:
        os.unlink(output)
