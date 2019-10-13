## 项目结构介绍
* analysis：答卷。
* assets：展示项目的图片和视频。
* RadiationVis：源代码，backend为后端代码，fronted为前端代码，使用 Django 和 Vue 实现前后端分离。

### RadiationVis/backend
后台代码，使用 Django 框架。

**如何将 csv 数据导入数据库？**

1. 根据 Excel 表头创建数据表
2. 将 csv 文件导入 MySQL 数据库
```
load data infile 'csvfilename.csv' into table tablename fields terminated by ',' enclosed by '"' lines terminated by '\r\n';
```
3. 根据数据库表，自动在 Django 中创建 Model
```
python manage.py inspectdb > appname/models.py
```

### RadiationVis/frontend
前端代码，使用 Vue 框架。

**Project setup**
```
npm install
```

**Compiles and hot-reloads for development**
```
npm run serve
```

**Compiles and minifies for production**
```
npm run build
```

**Run your tests**
```
npm run test
```

**Lints and fixes files**
```
npm run lint
```

**Customize configuration**

See [Configuration Reference](https://cli.vuejs.org/config/).


**Dependencies**

[vue](https://cn.vuejs.org/v2/guide/), [axios](https://www.kancloud.cn/yunye/axios/234845), [element-ui](http://element-cn.eleme.io/#/zh-CN), [d3](https://d3js.org/), [OpenLayers](https://openlayers.org/)

### RadiationVis/log
日志文件夹。

### RadiationVis/sql.zip
SQL 文件，用于创建数据库和添加数据。

