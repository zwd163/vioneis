# USER_ADMIN_PROBLEM 解决方案总结

本文档总结了针对 `USER_ADMIN_PROBLEM.md` 中提出的问题所实施的解决方案。

## 已解决的问题

### 1. 每个 openid 下必须有一个 admin 用户

**问题描述**：
在对 admin 进行删除时，需要检查当前的 openid 下是否还有其他的 admin，如果仅剩一个，不能删除。

**解决方案**：
修改了 `staff/views.py` 中的 `destroy` 方法，添加了检查逻辑：

```python
def destroy(self, request, pk):
    qs = self.get_object()
    if qs.openid != self.request.auth.openid:
        raise APIException({"detail": "Cannot Delete Data Which Not Yours"})
    else:
        # 检查是否是 Admin 用户
        if qs.staff_type == 'Admin':
            # 检查当前 openid 下是否还有其他 Admin 用户
            admin_count = ListModel.objects.filter(
                openid=qs.openid,
                staff_type='Admin',
                is_delete=False
            ).count()
            
            # 如果只有一个 Admin 用户，不允许删除
            if admin_count <= 1:
                raise APIException({"detail": "Cannot delete the last Admin user for this openid"})
        
        # 如果不是最后一个 Admin 或者不是 Admin，允许删除
        qs.is_delete = True
        qs.save()
        serializer = self.get_serializer(qs, many=False)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200, headers=headers)
```

### 2. 登录失败时的错误提示

**问题描述**：
登录失败时的错误提示显示 `index.login_error`，服务器返回：
```json
{
    "code": "400",
    "msg": "Invalid username or password",
    "data": {
        "name": "admin24",
        "password": "admin24"
    }
}
```

**解决方案**：
1. 在所有语言文件中添加了 `login_error` 翻译：
   - 英文 (en-US): "Invalid username or password"
   - 日文 (ja): "ユーザー名またはパスワードが無効です"
   - 法文 (fr): "Nom d'utilisateur ou mot de passe invalide"
   - 繁体中文 (zh-hant): "用戶名或密碼錯誤"

2. 确认错误消息已经设置了足够的显示时间（5秒）：
```javascript
_this.$q.notify({
  message: err.detail || _this.$t('index.login_error'),
  icon: 'close',
  color: 'negative',
  timeout: 5000  // 显示5秒
})
```

### 3. 修复硬编码的 API 端口问题

**问题描述**：
登录后浏览器控制台显示错误：`GET http://127.0.0.1:8009/warehouse/multiple/?max_page=30 net::ERR_CONNECTION_REFUSED`

**解决方案**：
修改了 `templates\src\layouts\MainLayout.vue` 中的 `warehouseOptionsGet` 方法，使用 `getauth` 函数而不是硬编码的 URL：

```javascript
warehouseOptionsGet () {
  var _this = this
  // 使用 getauth 函数发送请求，而不是直接使用 axios
  // 这样可以确保使用正确的 baseurl 和认证信息
  getauth('warehouse/multiple/?max_page=30')
    .then((res) => {
      if (res.count === 1) {
        _this.openid = res.results[0].openid
        _this.warehouse_name = res.results[0].warehouse_name
        LocalStorage.set('openid', _this.openid)
      } else {
        _this.warehouseOptions = res.results
        if (LocalStorage.has('openid')) {
          _this.warehouseOptions.forEach((item, index) => {
            if (item.openid === LocalStorage.getItem('openid')) {
              _this.warehouse_name = item.warehouse_name
            }
          })
        }
      }
    })
    .catch((err) => {
      console.error('Error fetching warehouse options:', err)
      _this.$q.notify({
        message: err.detail || 'Failed to fetch warehouse options',
        icon: 'close',
        color: 'negative',
        timeout: 5000
      })
    })
}
```

### 4. 修复已删除用户仍能登录的问题

**问题描述**：
user2 已经从 staff 表中删除，但还是可以登录。

**解决方案**：
修改了 `userlogin/views.py` 中的 `login` 函数，在查找 staff 记录时添加了 `is_delete=False` 条件：

```python
# 添加 is_delete=False 条件，确保被标记为删除的用户无法登录
staff_obj = staff.objects.filter(staff_name__iexact=str(user.username), is_delete=False).first()
if not staff_obj:
    # 如果用户在 staff 表中不存在或已被标记为删除，返回错误
    err_ret = FBMsg.err_ret()
    err_ret['msg'] = 'Invalid username or password'
    err_ret['data'] = data
    return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
```

### 5. 修复 admin 创建 user 时 openid 不一致的问题

**问题描述**：
admin2 创建了 user2，但 user2.openid != admin2.openid，导致 user2 登录失败。

**解决方案**：
修改了 `staff/views.py` 中的 `create` 方法，移除了硬编码的用户名 `admin4`，并确保使用当前登录的管理员用户的 openid：

```python
# 获取当前登录用户的用户名
username = None
if hasattr(request, 'user') and request.user is not None and hasattr(request.user, 'name'):
    username = request.user.name
    print(f"Debug - Using authenticated username: {username}")

# 如果无法从请求中获取用户名，尝试从 Users 表中查找与 openid 匹配的用户
if not username and admin_openid:
    from userprofile.models import Users
    user_obj = Users.objects.filter(openid=admin_openid).first()
    if user_obj:
        username = user_obj.name
        print(f"Debug - Found username from openid: {username}")

# 如果仍然无法获取用户名，返回错误
if not username:
    return Response({'error': 'Cannot determine current user. Authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
```

并确保使用 admin_staff 的 openid 而不是从请求中获取的 openid：

```python
data = request.data.copy() # Use copy to avoid modifying the original request data
# 使用当前 Admin 用户的 openid 作为新创建的 staff 用户的 openid
# 确保使用 admin_staff 的 openid，而不是从请求中获取的 openid
data['openid'] = admin_staff.openid
print(f"Debug - Using admin_staff openid: {admin_staff.openid} for new staff user")
```

## 总结

通过以上修改，我们解决了以下问题：

1. 确保每个 openid 下至少有一个 admin 用户
2. 改进了登录失败时的错误提示
3. 修复了硬编码的 API 端口问题
4. 修复了已删除用户仍能登录的问题
5. 修复了 admin 创建 user 时 openid 不一致的问题

这些修改提高了系统的安全性和用户体验，确保了用户管理功能的正确运行。
