# 用户管理和认证问题

## 问题概述
1. staff 和 user_auth 表都有 email 字段，需要合并到 staff 表中。删除 auth_user 中的email字段。
2. openid 只在 admin 注册中时产生，staff 的 openid，在admin添加用户时，填写当前admin.openid
3. 每个admin 只能看到和自己openid 相同的记录，不能看到其他admin 的记录
4. 所有用户，只能查看或者增删改查和自己相同的openid 的记录
5. admin 注册需要email address
**日期:** 2025-04-05
**类型:** 开发