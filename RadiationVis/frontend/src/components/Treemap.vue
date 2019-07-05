<template>
  <div :id="cid">
    <div class="treemap"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import axios from '../assets/js/http'
export default {
  name: 'Treemap',
  props: {
    cid: String,
    originData: Object
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
      timeRange: null,
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
      sidList: [],
    }
  },
  created: function () {
      // this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
      // this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
   },
  mounted() {
    this.$nextTick(() => {
      this.loadChart();
    })
  },
  methods: {
    loadChart() {
      this.selfAdaptionSvgSize();
      this.drawSvg();
      if(this.originData) {
        if(this.originData.state == 'treemap1') {
          this.drawTreemap1();
        } else {
          this.drawTreemap2();
        }
      }
    },
    selfAdaptionSvgSize() {
      let container = document.querySelector(`#${this.cid}`);
      let parentNode = container.parentNode;
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .treemap`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawTreemap1() {
      let margin = { top: 5, right: 5, bottom: 5, left: 5 },
            chartWidth  = this.svgWidth  - margin.left - margin.right,
            chartHeight = this.svgHeight - margin.top  - margin.bottom;

      let g = this.svg.append("g").attr("transform", "translate(" + (margin.left) + "," + (margin.top) + ")");

      let fader = function(color) { return d3.interpolateRgb(color, "#fff")(0.2); },
        color = d3.scaleOrdinal(d3.schemeCategory10.map(fader)),
        format = d3.format(",d");

      let treemap = d3.treemap()
          .tile(d3.treemapBinary)
          .size([chartWidth, chartHeight])
          .round(true)
          .paddingInner(1);

      let data = JSON.parse(JSON.stringify(this.originData.data));

      data.children.forEach(d => {
        d.children.sort((a, b) => b.mean-a.mean)
      })
      let max2list = [];
      data.children.forEach(d => {
        max2list.push(d.children.slice(0, d.children.length > 2 ? 2: d.children.length))
      })
      max2list = max2list.flat();
      max2list.sort((a, b) => b.mean - a.mean)
      let category1 = max2list[0].name.startsWith("s") ? "static": "mobile";
      let category2 = max2list[1].name.startsWith("s") ? "static": "mobile";
      let sid1 = max2list[0].name.substring(1, max2list[0].name.length);
      let sid2 = max2list[1].name.substring(1, max2list[1].name.length);
      this.$root.eventHub.$emit("sensorSelected", Object.assign({}, {category: category1, sid: sid1}, this.originData.timeRange||this.defaultTimeRange));
      this.$root.eventHub.$emit("sensorSelected", Object.assign({}, {category: category2, sid: sid2}, this.originData.timeRange||this.defaultTimeRange));

      let sensors = data.children.map(d => {
        let category = d.children[0].name.startsWith('s') ? "static": "mobile";
        let sid = d.children[0].name.substring(1);
        return {category: category, sid: sid};
      })

      let cluster = {name: 'cluster', children: []};
      let childrenLength = data.children.length;
      for(let i=0; i<childrenLength; i++) {
        cluster.children[i] = {};
        cluster.children[i].name = "cluster" + i;
        cluster.children[i].mean = d3.mean(data.children[i].children, d => d.mean);
        cluster.children[i].std = d3.mean(data.children[i].children, d => d.std);
        cluster.children[i].static = data.children[i].children.filter(d => d.name.startsWith('s'));
        cluster.children[i].mobile = data.children[i].children.filter(d => d.name.startsWith('m'));
        cluster.children[i].lineExample = sensors[i];
      }
      console.log(cluster);
      var root = d3.hierarchy(cluster)
          .eachBefore(function(d) { d.data.id = d.data.name; })
          .sum(d => d.mean)
          .sort(function(a, b) { return b.height - a.height || b.value - a.value; });

      treemap(root);

      var cell = g.selectAll("g")
        .data(root.leaves())
        .enter().append("g")
          .attr("transform", function(d) { return "translate(" + d.x0 + "," + d.y0 + ")"; })
          .on("click", (d, i) => {
            // this.drawTreemap2(data.children[i])
            this.$root.eventHub.$emit("getTreemap2", data.children[i]);

          })

      cell.append("rect")
          .attr("id", function(d) { return d.data.id; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .attr("fill", "steelblue");
          // .attr("fill", function(d) { return color(d.parent.data.id); });

      sensors.forEach((d, i) => {
        this.drawLineBySid(d3.select(cell.nodes()[i]), d)
      })

      cell.append("text")
          .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
        .selectAll(".treemap tspan")
          .data(function(d) { return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
        .enter().append("tspan")
          .attr("x", 4)
          .attr("y", function(d, i) { return 13 + i * 10; })
          .text(function(d, i) { let info = cluster.children.filter(s => s.name == d)[0]; return  `Static Sensor: ${info.static.length}, Mobile Sensor: ${info.mobile.length}` })
          .style("font-size", 12);
      
    },
    drawTreemap2() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
      var margin = { top: 5, right: 5, bottom: 5, left: 5 },
            chartWidth  = this.svgWidth  - margin.left - margin.right,
            chartHeight = this.svgHeight - margin.top  - margin.bottom;

      let g = this.svg.append("g").attr("transform", "translate(" + (margin.left) + "," + (margin.top) + ")");

      var fader = function(color) { return d3.interpolateRgb(color, "#fff")(0.2); },
        color = d3.scaleOrdinal(d3.schemeCategory10.map(fader)),
        format = d3.format(",d");

      var treemap = d3.treemap()
          .tile(d3.treemapBinary)
          .size([chartWidth, chartHeight])
          .round(true)
          .paddingInner(1);

      var root = d3.hierarchy(this.originData.data)
            .eachBefore(function(d) { d.data.id = d.data.name; })
            .sum(d => d.mean)
            .sort(function(a, b) { return b.height - a.height || b.value - a.value; });

      treemap(root);

      var cell = g.selectAll("g")
        .data(root.leaves())
        .enter().append("g")
          .attr("transform", function(d) { return "translate(" + d.x0 + "," + d.y0 + ")"; })
          .on("click", (d, i) => {
            let category = null;
            let sid = null;
            if(d.data.name.startsWith("m")) {
              category = "mobile";
            } else {
              category = "static";
            }
            sid = parseInt(d.data.name.substring(1, d.data.name.length));
            this.$root.eventHub.$emit("sensorSelected", Object.assign({}, {category: category, sid: sid}, this.originData.timeRange||this.defaultTimeRange));
          })

      cell.append("rect")
          .attr("id", function(d) { return d.data.id; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .attr("fill", "steelblue");
          // .attr("fill", function(d) { return color(d.parent.data.id); });

      cell.append("text")
          .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
        .selectAll(".treemap tspan")
          .data(function(d) { return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
        .enter().append("tspan")
          .attr("x", 4)
          .attr("y", function(d, i) { return 13 + i * 10; })
          .text(function(d) { return d; })
          .style("font-size", 10);
    },
    drawLineBySid(g, sensor_info) {

      let _this = this;

      let datum = g.datum();

      function makeChartBySid (data) {
        var margin = { top: 0, right: 0, bottom: 0, left: 0 },
            chartWidth  = datum.x1 - datum.x0,
            chartHeight = datum.y1 - datum.y0 > 50 ? 50: datum.y1 - datum.y0;

        let begin = null, end = null;
        if(_this.timeRange != null) {
          begin = new Date(_this.timeRange.begintime);
          end = new Date(_this.timeRange.endtime);
        } else {
          begin = new Date(_this.defaultTimeRange.begintime);
          end = new Date(_this.defaultTimeRange.endtime);
        }

        let max = d3.max(data, d => d.avg);

        let x, y;

        if(end.getTime() - begin.getTime() > 12 * 3600 * 1000) {
          x = d3.scaleTime()
            .range([0, chartWidth])
            .domain([new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours()), new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours())]);
        } else {
          x = d3.scaleTime()
            .range([0, chartWidth])
            .domain([new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours(), begin.getMinutes()), new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours(), end.getMinutes())]);
        }

        y = d3.scaleLinear().range([chartHeight, 0])
              .domain([0, max]);


        var line_g = g.append('g')
            .attr('transform', d => 'translate(' + margin.left + ',' + (margin.top + (d.y1-d.y0) * 0.35) + ')');

        let medianLine = d3.line()
          .x(function (d) { return x(d.time); })
          .y(function (d) { return y(d.avg); })
          .curve(d3.curveMonotoneX);


        line_g.datum(data);

        line_g.append('path')
          .attr("class", "line")
          .attr('d', medianLine);

      }
      
      /***************************************************************************************/

      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", Object.assign({}, this.timeRange || this.defaultTimeRange, sensor_info))
        .then((response) => {
          var data = response.data.map(function (d) {
            return {
              time:  parseDate(d.time),
              avg: parseFloat(d.avg),
            };
          });
          makeChartBySid(data);
        })
    },
    clearAllg() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
    },
    // timeRangeUpdated(params) {
    //   this.timeRange = params;
    //   d3.select(`#${this.cid} svg`).selectAll('g').remove();
    //   this.drawTreemap1();
    // }
  },
  watch: {
    originData: {
      handler(n, o) {
        this.clearAllg();
        if(n) {
          if(n.state == 'treemap1') {
            this.drawTreemap1();
          } else {
            this.drawTreemap2();
          }
        }
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.treemap >>> .label {
  font-size: 8px;
}
.treemap >>> path {
  fill: none;
  stroke: black;
  stroke-width: 1;
}
</style>
