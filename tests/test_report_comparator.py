import pytest
import os
import tempfile
import csv
from common.report_comparator import ReportComparator


@pytest.fixture
def sample_csv_files():
    """创建样本 CSV 文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "report1.csv")
        file2 = os.path.join(tmpdir, "report2.csv")

        with open(file1, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["股票代码", "价格", "数量"])
            writer.writerow(["600000", "10.5", "100"])
            writer.writerow(["600001", "20.0", "200"])

        with open(file2, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["股票代码", "价格", "数量"])
            writer.writerow(["600000", "10.5", "100"])
            writer.writerow(["600001", "20.5", "200"])

        yield file1, file2


def test_compare_csv_no_diff():
    """测试相同 CSV 无差异"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "a.csv")
        file2 = os.path.join(tmpdir, "b.csv")
        for f in (file1, file2):
            with open(f, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["id", "value"])
                writer.writerow(["1", "100"])

        comp = ReportComparator()
        result = comp.compare_csv(file1, file2)
        assert result["diff_count"] == 0
        assert result["is_equal"] is True


def test_compare_csv_with_diff(sample_csv_files):
    """测试有差异的 CSV"""
    file1, file2 = sample_csv_files
    comp = ReportComparator()
    result = comp.compare_csv(file1, file2)
    assert result["diff_count"] > 0
    assert result["is_equal"] is False
    assert len(result["diffs"]) > 0


def test_generate_diff_report(sample_csv_files):
    """测试生成差异报告"""
    file1, file2 = sample_csv_files
    comp = ReportComparator()

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        output = f.name

    try:
        comp.generate_diff_report(file1, file2, output)
        assert os.path.exists(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        assert "报表对比报告" in content
    finally:
        os.unlink(output)
