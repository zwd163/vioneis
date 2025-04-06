# 程序初始化

## 问题概述

**日期:** 2025-04-05
**类型:** 开发

**问题描述:** 
1. 去除  templates\src\boot\vueMain.js 中多余的 console.log
2. 修改： templates\quasar.conf.js 中builder.url
3. templates\src\index.template.html 中修改 keywords
4. templates\src\pages\warehouse\warehouseset.vue line:584, 605, 都有： axios.put('https://po.56yhz.com/warehouse/', _this.publishdetail，  待去除
5. templates\src\layouts\MainLayout.vue  line:31, 49, 67, 85, 有以下内容： @click="brownlink('https://www.56yhz.com/md/ios/zh-CN')",  待去除