"""性能回归门槛：headless 跑 locust，断言 0 失败 + p95 < 阈值。

这是普通 pytest 测试，复用现有 locustfile.py 与 CI 的 pytest 步骤，
无需在 YAML 里单独编排 locust。
"""
import csv
import os
import subprocess
import sys
import tempfile

import pytest

from common.process_utils import start_service

pytestmark = pytest.mark.performance

P95_THRESHOLD_MS = 2000  # 宽松阈值：慢 CI 能过，但拦灾难性回归


def _locust_stats_csv_prefix(tmpdir):
    return os.path.join(tmpdir, "locust_report")


def test_api_performance_p95_under_threshold():
    """对本地 mock 跑 10 并发 15s，断言无失败且 p95 达标"""
    proc = start_service("mock_services.api_mock", "127.0.0.1", 5000)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix = _locust_stats_csv_prefix(tmpdir)
            cmd = [
                sys.executable, "-m", "locust",
                "-f", "tests/performance/locustfile.py",
                "--headless",
                "-u", "10",
                "-r", "10",
                "-t", "15s",
                "--host", "http://127.0.0.1:5000",
                "--csv", prefix,
                "--only-summary",
            ]
            result = subprocess.run(
                cmd,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0, (
                f"locust 退出码非 0:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )

            stats_path = prefix + "_stats.csv"
            assert os.path.exists(stats_path), f"未找到 locust 统计 CSV: {stats_path}"

            # _stats.csv 结构：首行是 "Type","Name" ... 的表头，
            # 第一类聚合行 Name=="Aggregated"
            with open(stats_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                agg = None
                for row in reader:
                    if row.get("Name") == "Aggregated":
                        agg = row
                        break

            assert agg is not None, "未找到 Aggregated 聚合行"
            failures = int(float(agg.get("Failure Count", 0)))
            p95 = float(agg.get("95%", "0").replace(",", ""))

            assert failures == 0, f"性能测试出现 {failures} 个失败请求"
            assert p95 < P95_THRESHOLD_MS, (
                f"p95={p95}ms 超过阈值 {P95_THRESHOLD_MS}ms"
            )
    finally:
        proc.terminate()
        proc.wait()
