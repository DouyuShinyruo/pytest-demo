Feature: 用户登录
  作为用户
  我需要通过登录页面登录系统
  以便访问受保护的资源

  Scenario: 正常登录
    Given 我打开登录页面
    When 我输入用户名 "admin" 和密码 "123456"
    And 我点击登录按钮
    Then 我应该跳转到控制台页面
    And 页面显示 "admin"

  Scenario: 密码错误
    Given 我打开登录页面
    When 我输入用户名 "admin" 和密码 "wrong"
    And 我点击登录按钮
    Then 我应该看到错误提示 "错误"
