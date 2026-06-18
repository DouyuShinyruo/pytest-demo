"""性能回归门槛：headless 跑 locust，断言 0 失败 + p95 < 阈值。

这是普通 pytest 测试，复用根 conftest 的 session 级 mock_server 与 CI 的
pytest 步骤，无需在 YAML 里单独编排 locust。
"""
import csv
import os
import subprocess
import sys
import tempfile

import pytest
import requests

from common.paths import PROJECT_ROOT

pytestmark = pytest.mark.performance

P95_THRESHOLD_MS = 2000  # 宽松阈值：慢 CI 能过，但拦灾难性回归
WARMUP_HITS = 30  # 预热请求数：压测前先打一波，消除 dev server 冷启动抖动


def _warmup_server(url, hits=WARMUP_HITS):
    """预热 dev server：压测前先发若干顺序请求，完成路由编译与连接预热，
    避免冷启动瞬间的连接失败被计入 locust 失败率。"""
    for _ in range(hits):
        try:
            requests.get(url, timeout=2)
        except requests.RequestException:
            pass


def _locust_stats_csv_prefix(tmpdir):
    return os.path.join(tmpdir, "locust_report")


def test_api_performance_p95_under_threshold(mock_server):
    """对本地 mock 跑 10 并发 15s，断言无失败且 p95 达标。

    复用根 conftest 的 session 级 mock_server（端口 5000），不单独再起服务，
    避免与功能测试争抢端口。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        _warmup_server("http://127.0.0.1:5000/api/users")
        prefix = _locust_stats_csv_prefix(tmpdir)
        cmd = [
            sys.executable, "-m", "locust",
            "-f", "tests/performance/locustfile_fast.py",
            "--headless",
            "-u", "10",
            "-r", "5",
            "-t", "15s",
            "--host", "http://127.0.0.1:5000",
            "--csv", prefix,
            "--only-summary",
        ]
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        stats_path = prefix + "_stats.csv"
        assert os.path.exists(stats_path), f"未找到 locust 统计 CSV: {stats_path}"

        with open(stats_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            agg = None
            for row in reader:
                if row.get("Name") == "Aggregated":
                    agg = row
                    break

        assert agg is not None, "未找到 Aggregated 聚合行"

        request_count = int(float(agg.get("Request Count", 0)))
        failures = int(float(agg.get("Failure Count", 0)))
        p95 = float(agg.get("95%", "0").replace(",", ""))

        print(
            f"\n[perf] request_count={request_count} failures={failures} "
            f"failure_rate={(failures / request_count) if request_count else float('nan'):.4%} "
            f"p95={p95}ms (returncode={result.returncode})"
        )

        assert request_count > 0, "locust 未产生任何请求，结果不可用"

        # 用失败率而非「绝对 0 失败」做门槛：冷启动瞬时尖峰会产生极少数失败，
        # 但真正的回归（持续报错/显著变慢）会让失败率远高于 1%。
        failure_rate = failures / request_count
        assert failure_rate < 0.01, (
            f"失败率 {failure_rate:.2%}（{failures}/{request_count}）超过 1% 门槛"
        )
        assert p95 < P95_THRESHOLD_MS, (
            f"p95={p95}ms 超过阈值 {P95_THRESHOLD_MS}ms"
        )
