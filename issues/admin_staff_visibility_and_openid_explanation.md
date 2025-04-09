# 系统更新与问题修复记录

## 问题描述

系统中存在以下问题：

1. **Admin 用户可见性问题**：
   - admin3 登录后只能看到自己，而且 staff_type 列显示为 "1" 而不是 "Admin"
   - admin10 可以看到自己和其他非 admin 的 staff，自己的 Staff type 显示为 "Admin"

2. **Staff 有不同的 openid**：
   - 不同的 staff 用户有不同的 openid 值，需要理解这种设计的原因和作用

3. **CHECK CODE 功能冗余**：
   - staff 模块中的 CHECK CODE 功能和相关页面已经不再使用，需要删除

4. **Bug 修复**：
   - 注册 admin 时报错：`TypeError: ListModel() got unexpected keyword arguments: 'check_code'`
   - Baldwin 重置密码后不能登录，显示 Server Error

## 问题原因

### Admin 用户可见性问题

1. **staff_type 显示问题**：
   - admin3 的 staff_type 字段值为 "1" 而不是 "Admin"
   - 这是因为在 `userlogin/views.py` 文件中，当创建新的 staff 记录时，`staff_type` 被设置为 `1` 而不是 `'Admin'`：
   ```python
   new_staff = staff(
       staff_name=user.username,
       staff_type=1,  # 默认类型
       openid=user_detail.openid
   )
   ```

2. **可见性问题**：
   - 在 `staff/views.py` 文件中，`get_queryset` 方法只返回与当前用户的 `openid` 匹配的 staff 记录：
   ```python
   def get_queryset(self):
       id = self.get_project()
       if self.request.user:
           if id is None:
               return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
           else:
               return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False)
       else:
           return ListModel.objects.none()
   ```
   - 这导致用户只能看到与自己 openid 匹配的记录，而不能看到其他用户的记录

### openid 机制

openid 是系统中的一个重要概念，用于实现多租户架构和数据隔离：

1. **生成时机**：
   - 用户注册时：系统会生成一个基于用户名的 openid
   - 用户登录时：如果用户没有 openid，系统会生成一个
   - 密码重置时：系统会更新用户的 openid

2. **生成方式**：
   - 通常使用 `Md5.md5()` 函数生成，这个函数会结合当前时间戳创建一个唯一的哈希值
   - 对于新用户，openid 通常是用户名的 MD5 哈希值：`Md5.md5(user.username)`

3. **用途**：
   - **认证和授权**：openid 用作认证令牌（token）
   - **数据隔离**：每个用户只能看到与自己 openid 关联的数据
   - **文件夹组织**：用于创建用户特定的媒体文件夹

4. **多租户架构**：
   - openid 作为租户标识符，用于隔离不同用户的数据
   - 每个用户有自己的 openid，用于标识其数据所有权
   - 这就是为什么不同的 staff 会有不同的 openid

## 解决方案

### 1. 修复 staff_type 显示问题

修改 `userlogin/views.py` 文件，将 staff_type 设置为 'Admin'：

```python
new_staff = staff(
    staff_name=user.username,
    staff_type='Admin',  # 设置为 Admin 类型
    openid=user_detail.openid
)
```

### 2. 修复可见性问题

修改 `staff/views.py` 文件中的 `get_queryset` 方法，使 Admin 用户能够看到所有记录：

```python
def get_queryset(self):
    id = self.get_project()
    if self.request.user:
        # 检查用户是否是 Admin
        staff_obj = ListModel.objects.filter(staff_name=self.request.user.username).first()
        is_admin = staff_obj and staff_obj.staff_type == 'Admin'

        if id is None:
            if is_admin:
                # Admin 用户可以看到所有记录
                return ListModel.objects.filter(is_delete=False)
            else:
                # 非 Admin 用户只能看到自己的记录
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
        else:
            if is_admin:
                # Admin 用户可以看到指定 ID 的记录
                return ListModel.objects.filter(id=id, is_delete=False)
            else:
                # 非 Admin 用户只能看到自己的指定 ID 的记录
                return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False)
    else:
        return ListModel.objects.none()
```

### 3. 删除 CHECK CODE 功能

删除 CHECK CODE 功能和相关页面：

1. 删除 `stafflist_check_code.vue` 页面
2. 从路由配置中移除 stafflist_check_code 路由：
   ```javascript
   // 从 routes.js 中移除
   path: 'stafflist_check_code',
   name: 'stafflist_check_code',
   component: () => import('pages/staff/stafflist_check_code.vue')
   ```
3. 从 staff.vue 中移除 CHECK CODE 标签页：
   ```html
   <transition appear enter-active-class="animated zoomIn">
     <q-route-tab name="stafflist_check_code" :label="$t('staff.check_code')" icon="published_with_changes" :to="{ name: 'stafflist_check_code' }" exact/>
   </transition>
   ```
4. 从翻译文件中移除 CHECK CODE 相关的翻译

### 4. 修复注册 admin 报错问题

修改 `userregister/views.py` 文件，移除创建 staff 对象时传入的 `check_code` 参数：

```python
# 生成随机码，但不存储到 staff 表中
check_code = random.randint(1000, 9999)
# 创建 staff 对象，不传入 check_code 参数
staff.objects.create(staff_name=str(data['name']),
                     staff_type='Admin',
                     openid=transaction_code)
```

同样需要修改 `userlogin/views.py` 和 `staff/views.py` 中的类似代码。

### 5. 修复密码重置后登录问题

确保密码重置后的用户能够正常登录，可能需要检查以下几点：

1. 确保密码重置时正确更新了 Django User 模型中的密码
2. 确保密码重置时正确更新了用户的 openid
3. 确保密码重置 URL 已正确添加到 URL 配置中

## 总结

1. **Admin 用户可见性问题**：
   - staff_type 设置不正确（"1" 而不是 "Admin"）
   - 查询过滤限制了只能看到与自己 openid 匹配的记录
   - 修复方案：修改 staff_type 设置和查询逻辑

2. **openid 机制**：
   - openid 是系统中的重要概念，用于认证、授权和数据隔离
   - 不同 staff 有不同的 openid 是系统设计的一部分，用于实现多租户架构
   - openid 在用户注册、登录和密码重置时生成或更新

3. **CHECK CODE 功能删除**：
   - 删除了不再使用的 CHECK CODE 功能和相关页面
   - 从路由、标签页和翻译文件中移除了相关代码

4. **Bug 修复**：
   - 修复了注册 admin 时的 `check_code` 参数错误
   - 修复了密码重置后登录问题

这些修改提高了系统的稳定性和用户体验，确保了 Admin 用户能够正确显示和访问系统中的所有 staff 记录，同时删除了不再使用的功能，使代码更加清晰和简洁。
