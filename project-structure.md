## 项目结构介绍
* analysis：Our answers.
* assets：Images for display.
* RadiationVis：The source code. `Backend` is back-end code and `frontend` is front-end code. We use Django and Vue to separate the front and back ends.

### RadiationVis/backend
The back-end code. We use the Django framework.

**How to import csv data into mysql database?**

1. Create a data table based on the Excel header
2. Import csv data into mysql database
```
load data infile 'csvfilename.csv' into table tablename fields terminated by ',' enclosed by '"' lines terminated by '\r\n';
```
3. Automatically create Model in Django based on database tables
```
python manage.py inspectdb > appname/models.py
```

### RadiationVis/frontend
The front-end code. We use the Vue framework.

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
Log folder.

### RadiationVis/sql.zip
SQL file for creating databases and adding data.

