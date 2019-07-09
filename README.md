# vast-challenge-2019-MC2
VAST Challenge 2019: Mini-Challenge 2

使用 Django 和 Vue 实现前后端分离。

## backend - 后台

1. 根据 Excel 表头创建数据
2. 将 csv 文件导入 MySQL 数据库
```
load data infile 'csvfilename.csv' into table tablename fields terminated by ',' enclosed by '"' lines terminated by '\r\n';
```
3. 根据数据库表，自动在 Django 的 Model
```
python manage.py inspectdb > appname/models.py
```

## frontend - 前端

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

## sql.zip
SQL 文件，用于创建数据库和添加数据。

