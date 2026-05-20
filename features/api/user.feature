Feature: 用户管理 API
  作为测试人员
  我需要验证用户 API 的功能
  以便确保接口正常工作

  Scenario: 正常创建用户
    Given 我有有效的用户数据 "张三"
    When 我调用创建用户接口
    Then 返回状态码 201
    And 返回的用户名称为 "张三"

  Scenario: 创建用户时用户名为空
    Given 我有空的用户名
    When 我调用创建用户接口
    Then 返回状态码 400

  Scenario: 获取用户列表
    Given 系统中已有用户 "张三"
    When 我调用获取用户列表接口
    Then 返回状态码 200
    And 返回的列表长度为 1
