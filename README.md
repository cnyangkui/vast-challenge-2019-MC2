# vast-challenge-2019-MC2
VAST Challenge 2019: Mini-Challenge 2

挑战赛背景和题目介绍：[https://vast-challenge.github.io/2019/MC2.html](https://vast-challenge.github.io/2019/MC2.html)

## 界面展示

**Video**

![avatar](/assets/video.gif)

**Case study 1**

![avatar](/assets/Case1.jpg)

**Case study 2**

![avatar](/assets/Case2.jpg)

**Case study 3**

![avatar](/assets/Case3.jpg)

## 项目结构介绍

* assets：展示项目的图片和视频。
* RadiationVis：源代码，backend为后端代码，fronted为前端代码，使用 Django 和 Vue 实现前后端分离。

### backend - 后台

1. 根据 Excel 表头创建数据表
2. 将 csv 文件导入 MySQL 数据库
```
load data infile 'csvfilename.csv' into table tablename fields terminated by ',' enclosed by '"' lines terminated by '\r\n';
```
3. 根据数据库表，自动在 Django 中创建 Model
```
python manage.py inspectdb > appname/models.py
```

### frontend - 前端

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

### sql.zip
SQL 文件，用于创建数据库和添加数据。

