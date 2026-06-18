# Pytest 自动化测试框架

一个模块化的 Python 测试框架，覆盖 API 测试、Web UI 测试、金融协议测试、性能测试等多种场景。

## 技术栈

| 类别 | 技术 |
|------|------|
| 测试框架 | pytest |
| API 测试 | requests |
| Web 测试 | Playwright |
| 协议测试 | socket（STEP 协议） |
| 性能测试 | Locust |
| BDD | pytest-bdd |
| 数据驱动 | PyYAML + pytest.mark.parametrize |
| Mock 服务 | Flask |
| 报告 | pytest-html / Allure |
| CI/CD | Jenkins / GitLab CI |
| 容器化 | Docker / docker-compose |

## 项目结构

```
pytest-framework/
├── common/                    # 工具库
│   ├── config.py              # 配置管理
│   ├── paths.py               # 项目根路径（消除 CWD 依赖）
│   ├── process_utils.py       # 服务进程启动 / 端口等待 / 清理
│   ├── logger.py              # 日志封装
│   ├── data_loader.py         # YAML 数据加载
│   ├── report_comparator.py   # 报表对比工具
│   └── allure_helper.py       # Allure 辅助
├── config/config.yaml         # 环境配置
├── mock_services/             # Mock 服务
│   ├── api_mock.py            # REST API Mock
│   ├── web_mock.py            # Web 页面 Mock
│   └── step_gateway_mock.py   # STEP 交易网关 Mock
├── tests/                     # 测试用例
│   ├── api/                   # API 接口测试
│   ├── web/                   # Web UI 测试
│   ├── protocol/              # STEP 协议测试
│   ├── reports/               # 报表对比测试
│   └── performance/           # Locust 性能测试（含门槛回归）
├── step_defs/                 # BDD 步骤实现
├── features/                  # BDD 场景文件
├── test_data/                 # 测试数据（YAML / CSV）
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
└── .gitlab-ci.yml
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 运行测试

```bash
# 运行全部测试
pytest tests/ step_defs/ -v

# 只运行 API 测试
pytest tests/api/ -v

# 只运行协议测试
pytest tests/protocol/ -v

# 运行 BDD 场景
pytest step_defs/ -v
```

### 3. 生成报告

```bash
# HTML 报告（默认生成在 reports/report.html）
pytest tests/ --html=reports/report.html --self-contained-html

# Allure 报告
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 4. Docker 运行

```bash
# 一键启动所有 Mock 服务并运行测试
docker-compose up --build
```

### 5. 性能测试

性能门槛回归以普通 pytest 测试形式运行（CI 自动执行）：自动启动本地 mock，
headless 跑 Locust，断言失败率与 p95 达标。

```bash
# 运行性能门槛回归（自动起 mock + 跑 locust + 校验阈值）
pytest tests/performance/ -v

# 交互式压测（手动启动 mock 后用 Locust Web UI）
python mock_services/api_mock.py &
locust -f tests/performance/locustfile.py --host=http://localhost:5000
```

## 测试覆盖

| 模块 | 测试类型 | 数量 |
|------|---------|------|
| API 测试 | 手写 + YAML 数据驱动 | 10 |
| Web UI 测试 | Playwright 登录流程 | 6 |
| STEP 协议测试 | 报单/撤单/查询 | 6 |
| BDD 场景 | API + Web | 5 |
| 报表对比 | CSV 差异检测（单元 + 集成） | 9 |
| 性能测试 | Locust 门槛回归 | 1 |
| 工具库单元测试 | config/paths/process_utils/logger/data_loader/report_comparator | 16 |
| **总计** | | **53** |

## CI/CD

项目同时支持 Jenkins 和 GitLab CI：

- **Jenkins**：使用 `Jenkinsfile`，发布 HTML、JUnit 报告并生成 Allure 静态报告
- **GitLab CI**：使用 `.gitlab-ci.yml`，支持缓存、artifact 归档与 Allure 报告生成

## 报表对比工具

内置 CSV 报表对比工具，支持逐行对比和 HTML 差异报告生成：

```python
from common.report_comparator import ReportComparator

comp = ReportComparator()

# 默认：按行号顺序对齐
result = comp.compare_csv("expected.csv", "actual.csv")

# 按主键列对齐（行顺序无关，适合乱序报表）
result = comp.compare_csv("expected.csv", "actual.csv", key_column="股票代码")

# 生成 HTML 差异报告（单元格内容自动转义，防 XSS）
comp.generate_diff_report("expected.csv", "actual.csv", "diff_report.html")
```
