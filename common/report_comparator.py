import csv
import os
from datetime import datetime


class ReportComparator:
    """报表对比工具，支持 CSV 对比和差异报告生成"""

    def compare_csv(self, file1, file2, key_column=None):
        """
        对比两个 CSV 文件

        Args:
            file1: 第一个 CSV 文件路径
            file2: 第二个 CSV 文件路径
            key_column: 用于行匹配的主键列名，None 时按行号匹配

        Returns:
            dict: 包含 diff_count, is_equal, diffs
        """
        rows1 = self._read_csv(file1)
        rows2 = self._read_csv(file2)

        headers1 = rows1[0] if rows1 else []
        headers2 = rows2[0] if rows2 else []

        if headers1 != headers2:
            return {
                "diff_count": 1,
                "is_equal": False,
                "diffs": [{"type": "header", "file1": headers1, "file2": headers2}],
            }

        data1 = rows1[1:] if len(rows1) > 1 else []
        data2 = rows2[1:] if len(rows2) > 1 else []

        diffs = []
        max_rows = max(len(data1), len(data2))

        for i in range(max_rows):
            row1 = data1[i] if i < len(data1) else None
            row2 = data2[i] if i < len(data2) else None

            if row1 is None:
                diffs.append({"type": "added", "row": i, "data": row2})
            elif row2 is None:
                diffs.append({"type": "removed", "row": i, "data": row1})
            elif row1 != row2:
                row_diffs = {}
                for j, (v1, v2) in enumerate(zip(row1, row2)):
                    if v1 != v2:
                        col = headers1[j] if j < len(headers1) else f"col_{j}"
                        row_diffs[col] = {"expected": v1, "actual": v2}
                if row_diffs:
                    diffs.append({"type": "modified", "row": i, "changes": row_diffs})

        return {
            "diff_count": len(diffs),
            "is_equal": len(diffs) == 0,
            "diffs": diffs,
        }

    def generate_diff_report(self, file1, file2, output_path):
        """
        生成 HTML 差异报告

        Args:
            file1: 第一个 CSV 文件路径
            file2: 第二个 CSV 文件路径
            output_path: 输出 HTML 文件路径
        """
        result = self.compare_csv(file1, file2)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>报表对比报告</title>
    <style>
        body {{ font-family: Microsoft YaHei, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .equal {{ color: green; }}
        .not-equal {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        .added {{ background: #e8f5e9; }}
        .removed {{ background: #ffebee; }}
        .modified {{ background: #fff3e0; }}
    </style>
</head>
<body>
    <h1>报表对比报告</h1>
    <div class="summary">
        <p><strong>文件 1:</strong> {os.path.basename(file1)}</p>
        <p><strong>文件 2:</strong> {os.path.basename(file2)}</p>
        <p><strong>差异数量:</strong> <span class="{'equal' if result['is_equal'] else 'not-equal'}">{result['diff_count']}</span></p>
        <p><strong>是否一致:</strong> <span class="{'equal' if result['is_equal'] else 'not-equal'}">{'是' if result['is_equal'] else '否'}</span></p>
        <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""

        if result["diffs"]:
            html += """
    <table>
        <tr>
            <th>行号</th>
            <th>类型</th>
            <th>详情</th>
        </tr>
"""
            for diff in result["diffs"]:
                row_num = diff.get("row", "-")
                diff_type = diff["type"]

                if diff_type == "header":
                    detail = f"表头不同: {diff['file1']} vs {diff['file2']}"
                    css_class = "modified"
                elif diff_type == "added":
                    detail = f"新增行: {diff['data']}"
                    css_class = "added"
                elif diff_type == "removed":
                    detail = f"删除行: {diff['data']}"
                    css_class = "removed"
                elif diff_type == "modified":
                    changes = diff["changes"]
                    parts = []
                    for col, vals in changes.items():
                        parts.append(f"{col}: {vals['expected']} → {vals['actual']}")
                    detail = ", ".join(parts)
                    css_class = "modified"
                else:
                    detail = str(diff)
                    css_class = ""

                html += f"""
        <tr class="{css_class}">
            <td>{row_num}</td>
            <td>{diff_type}</td>
            <td>{detail}</td>
        </tr>
"""
            html += "    </table>\n"

        html += """
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _read_csv(self, file_path):
        """读取 CSV 文件，返回二维列表"""
        rows = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        return rows
