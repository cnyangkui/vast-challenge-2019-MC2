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
      this.$root.eventHub.$emit("defaultSensors", Object.assign({}, {category: category1, sid: sid1}, this.originData.timeRange||this.defaultTimeRange));
      this.$root.eventHub.$emit("defaultSensors", Object.assign({}, {category: category2, sid: sid2}, this.originData.timeRange||this.defaultTimeRange));

      // let sensors = data.children.map(d => {
      //   let category = d.children[0].name.startsWith('s') ? "static": "mobile";
      //   let sid = d.children[0].name.substring(1);
      //   return {category: category, sid: sid};
      // })

      let cluster = {name: 'cluster', children: []};
      let childrenLength = data.children.length;
      for(let i=0; i<childrenLength; i++) {
        cluster.children[i] = {};
        cluster.children[i].name = data.children[i].name;
        cluster.children[i].mean = d3.mean(data.children[i].children, d => d.mean);
        cluster.children[i].std = d3.mean(data.children[i].children, d => d.std);
        cluster.children[i].static = data.children[i].children.filter(d => d.name.startsWith('s'));
        cluster.children[i].mobile = data.children[i].children.filter(d => d.name.startsWith('m'));
        // cluster.children[i].sensors = data.children[i].children;
      }

      let blurScale = d3.scaleLinear().domain([0, 400]).range([0, 36]);

      let blur_g = this.svg.append("g");
      // console.log(this.originData.data.children)
      cluster.children.forEach(d => {
        let defs = blur_g.append("defs").append('filter').attr("id", `filter-${d.name}`).attr("x", 0).attr("y", 0);
        defs.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", blurScale(d.std))
      })

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
            this.$root.eventHub.$emit("getTreemap2", {name: d.data.name, children: [d.data.static, d.data.mobile].flat()});

          })

      let colorScale;// = d3.scaleLinear().domain([20, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.originData.checkedState.length == 2 || (this.originData.checkedState.length == 1 && this.originData.checkedState[0] == 'mobile')) {
        colorScale = d3.scaleLinear().domain([20, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      }
      if(this.originData.checkedState.length == 1 && this.originData.checkedState[0] == 'static') {
        colorScale = d3.scaleLinear().domain([12, 20]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      }

      cell.append("rect")
          .attr("id", function(d) { return d.data.id; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .attr("fill", (d) => {
            return colorScale(d.data.mean);
          })
          .attr("opacity", 0.3)
          .style("filter", (d) => `url(#filter-${d.data.name})`);

      cluster.children.forEach((d, i) => {
        this.drawLineBySid(d3.select(cell.nodes()[i]))
      })

      cell.append("text")
          // .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
        .selectAll(".treemap tspan")
          .data(function(d) { 
            return `SS: ${d.data.static.length},MS: ${d.data.mobile.length}`.split(',')
            // return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
          })
        .enter().append("tspan")
          .attr("x", 4)
          .attr("y", function(d, i) { return 13 + i * 18; })
          .text(function(d, i) {  return d;})
          .style("font-size", 15);
      
    },
    drawTreemap2() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
      var margin = { top: 5, right: 5, bottom: 5, left: 5 },
            chartWidth  = this.svgWidth  - margin.left - margin.right,
            chartHeight = this.svgHeight - margin.top  - margin.bottom;

      let g = this.svg.append("g").attr("transform", "translate(" + (margin.left) + "," + (margin.top) + ")");

      
      let blurScale = d3.scaleLinear().domain([0, 400]).range([0, 36]);

      let blur_g = this.svg.append("g");
      // console.log(this.originData.data.children)
      this.originData.data.children.forEach(d => {
        let defs = blur_g.append("defs").append('filter').attr("id", `filter-${d.name}`).attr("x", 0).attr("y", 0);
        defs.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", blurScale(d.std))
      })

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

      let img = require('../assets/img/star.png');
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
      
      let colorScale;// = d3.scaleLinear().domain([20, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      if(this.originData.checkedState.length == 2 || (this.originData.checkedState.length == 1 && this.originData.checkedState[0] == 'mobile')) {
        colorScale = d3.scaleLinear().domain([20, 100]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      }
      if(this.originData.checkedState.length == 1 && this.originData.checkedState[0] == 'static') {
        colorScale = d3.scaleLinear().domain([12, 20]).range(["rgb(0,255,0)", "rgb(255,0,0)"]);
      }

      cell.append("rect")
          .attr("id", function(d) { return d.data.id; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          // .attr("fill", "steelblue");
          .attr("fill", d => colorScale(d.data.mean))
          .style("opacity", 0.3)
          .style("filter", (d) => `url(#filter-${d.data.name})`)

      cell.append("text")
          .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
        .selectAll(".treemap tspan")
          .data(function(d) { return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
        .enter().append("tspan")
          .attr("x", 4)
          .attr("y", function(d, i) { return 13 + i * 10; })
          .text(function(d) { return d; })

      let stdScale = d3.scaleQuantize().domain([0, 400]).range([1,2,3,4,5]);
      let completenessScale = d3.scaleQuantize().domain([0, 1]).range([1,2,3,4,5])
      let accuracyScale = d3.scaleQuantize().domain([0, 7]).range([1,2,3,4,5])
      let inconsistencyScale = d3.scaleQuantize().domain([0, 27.36]).range([0,1,2,3,4,5])


      cell.nodes().forEach(d => {
        let cell_ele = d3.select(d);
        let cell_data = cell_ele.datum();
        let std = stdScale(cell_data.data.std);
        let accuracy = accuracyScale(cell_data.data.accuracy);
        let completeness = completenessScale(cell_data.data.nan);
        let inconsistency = inconsistencyScale(cell_data.data.inconsistency)
        console.log(inconsistency)
        cell_ele.append("text")
            .attr("x", "0px")
             .attr("y", "20px")
             .attr("dy","1em")
             .text('u1')
        for(let m=0; m<std; m++) {
            cell_ele.append("image")
              .attr("xlink:href", img)
              .attr("x", (d, i) => `${m*10}px`)
              .attr("y", "20px")
              .attr("width", "10px")
              .attr("height", "10px");
        }
        for(let m=0; m<completeness; m++) {
            cell_ele.append("image")
              .attr("xlink:href", img)
              .attr("x", (d, i) => `${m*10}px`)
              .attr("y", "30px")
              .attr("width", "10px")
              .attr("height", "10px");
        }
        for(let m=0; m<accuracy; m++) {
            cell_ele.append("image")
              .attr("xlink:href", img)
              .attr("x", (d, i) => `${m*10}px`)
              .attr("y", "40px")
              .attr("width", "10px")
              .attr("height", "10px");
        }
        for(let m=0; m<inconsistency; m++) {
            cell_ele.append("image")
              .attr("xlink:href", img)
              .attr("x", (d, i) => `${m*10}px`)
              .attr("y", "50px")
              .attr("width", "10px")
              .attr("height", "10px");
        }
      })

    },
    drawUncertaintyMeasure(g, sensor_info){
      let _this = this;
      let datum = g.datum();





    },

    drawLineBySid(g) {

      let _this = this;

      let datum = g.datum();

      function makeChartBySid (data) {
        var margin = { top: 0, right: 10, bottom: 0, left: 10 },
            chartWidth  = datum.x1 - datum.x0 - margin.left - margin.right,
            chartHeight = datum.y1 - datum.y0 > 50 ? 50: datum.y1 - datum.y0;

        let begin = null, end = null;
        if(_this.originData.timeRange != null) {
          begin = new Date(_this.originData.timeRange.begintime);
          end = new Date(_this.originData.timeRange.endtime);
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
      let clusterSensors = [datum.data.static, datum.data.mobile].flat();
      let maxMeanSensor = null;
      let max = 0;
      for(let i=0, len=clusterSensors.length; i<len; i++) {
        if(clusterSensors[i].mean > 0) {
          max = clusterSensors[i].mean;
          maxMeanSensor = clusterSensors[i];
        }
      }
      let sensorInfo = {category: maxMeanSensor.name.startsWith('s')?'static':'mobile', sid: maxMeanSensor.name.substring(1)};
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", Object.assign({}, this.originData.timeRange || this.defaultTimeRange, sensorInfo))
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
