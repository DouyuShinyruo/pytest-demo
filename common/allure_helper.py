# common/allure_helper.py
import allure
import json


def attach_json(data, name="JSON Data"):
    """附加 JSON 数据到 allure 报告"""
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_text(text, name="Text"):
    """附加文本到 allure 报告"""
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)


def step(title):
    """allure 步骤装饰器"""
    return allure.step(title)
