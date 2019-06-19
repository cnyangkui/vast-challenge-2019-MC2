<template>
  <div :id="cid">
    <div class="trendchart"></div>
  </div>
</template>

<script>
import * as d3 from "d3"
import axios from '../assets/js/http';
export default {
  name: 'TrendChart',
  props: {
    cid: String
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
      sidDataList: [],
    }
  },
  created: function () {
      this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
      this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
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
      this.drawChart();
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector(`#${this.cid}`).parentNode;
      // console.log(parentNode.clientWidth, parentNode.clientHeight)
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .trendchart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    // params: {begintime: xxx, endtime: xxx}
    drawChart() {

      let _this = this;
    
      if (_this.timeRange == null) {
        var parseDate  = d3.timeParse('%Y-%m-%d %H:%M');
        d3.csv('/static/data/StaticSequenceStatistics.csv').then(staticData => {

          var static_data = staticData.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: parseFloat(d.lower95),
              avg: parseFloat(d.avg),
              upper95: parseFloat(d.upper95)
            };
          });

          d3.csv('/static/data/MobileSequenceStatistics.csv').then(mobileData => {
            var mobile_data = mobileData.map(function (d) {
              return {
                time:  parseDate(d.time),
                lower95: parseFloat(d.lower95),
                avg: parseFloat(d.avg),
                upper95: parseFloat(d.upper95)
              };
            });
            _this.makeChart(static_data, mobile_data);
          })
        });
      } else {
        let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
        axios.post("/calTimeSeries/", _this.timeRange)
          .then((response) => {
            let data = response.data;
            var static_data = data.static.map(function (d) {
              return {
                time:  parseDate(d.time),
                lower95: parseFloat(d.lower95),
                avg: parseFloat(d.avg),
                upper95: parseFloat(d.upper95)
              };
            });
            var mobile_data = data.mobile.map(function (d) {
              return {
                time:  parseDate(d.time),
                lower95: parseFloat(d.lower95),
                avg: parseFloat(d.avg),
                upper95: parseFloat(d.upper95)
              };
            });
            _this.makeChart(static_data, mobile_data);
          })
      }
    },
    addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight) {

      let axes = g.append('g')
        .attr('clip-path', 'url(#axes-clip)');

      axes.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);

      axes.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('(cpm)');

    },
    addLegend (g, chartWidth) {
      let legendWidth  = 70,
          legendHeight = 45;

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', -10)');

      legend.append('rect')
        .attr('class', 'legend-bg')
        .attr('width',  legendWidth)
        .attr('height', legendHeight);

      legend.append('rect')
        .attr('class', 'mobile_uncertainty')
        .attr('width',  20)
        .attr('height', 10)
        .attr('x', 5)
        .attr('y', 5);

      legend.append('text')
        .attr('x', 30)
        .attr('y', 15)
        .text('mobile');

      legend.append('rect')
        .attr('class', 'static_uncertainty')
        .attr('width',  20)
        .attr('height', 10)
        .attr('x', 5)
        .attr('y', 25);

      legend.append('text')
        .attr('x', 30)
        .attr('y', 35)
        .text('static');

      // legend.append('path')
      //   .attr('class', 'median-line')
      //   .attr('d', 'M10,80L85,80');

      // legend.append('text')
      //     .attr('x', 115)
      //     .attr('y', 85)
      //     .text('Median');
    },
    drawPaths (g, data, x, y, styleClass) {
      let upperInnerArea = d3.area()
        .x (function (d) { return x(d.time); })
        .y0(function (d) { return y(d.upper95); })
        .y1(function (d) { return y(d.avg); });

      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.avg); });

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.time); })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); });

      g.datum(data);

      g.append('path')
        .attr('class', 'area upper ' + styleClass)
        .attr('d', upperInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      g.append('path')
        .attr('class', 'area lower ' + styleClass)
        .attr('d', lowerInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      g.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine)
        .attr('clip-path', 'url(#rect-clip)');
    },
    makeChart(static_data, mobile_data) {
      let _this = this;

      let margin = { top: 10, right: 5, bottom: 30, left: 30 },
          chartWidth  = _this.svgWidth  - margin.left - margin.right,
          chartHeight = _this.svgHeight - margin.top  - margin.bottom;

      // let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      let begin = null, end = null;
      if(this.timeRange != null) {
        begin = new Date(this.timeRange.begintime);
        end = new Date(this.timeRange.endtime);
      } else {
        begin = new Date(this.defaultTimeRange.begintime);
        end = new Date(this.defaultTimeRange.endtime);
      }

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
            .domain([0, d3.max(mobile_data, function (d) { return d.upper95; })]);

      let xAxis = d3.axisBottom(x)
        .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10),
        // .tickFormat((d, i) => {
        //   if(i % 2 == 0) {
        //     if(i == 0 || static_data[i].date.getDate() != static_data[i-1].date.getDate()) {
        //       return `${d.getMonth()+1}/${d.getDate()}`;
        //     } else {
        //       return `${d.getHours()}`
        //     }
        //   }
        // }),
      yAxis = d3.axisLeft(y)
        .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10).ticks(3);

      let g = _this.svg.append('g')
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
      _this.addLegend(g, chartWidth);
      _this.drawPaths(g, static_data, x, y, "static_uncertainty");
      _this.drawPaths(g, mobile_data, x, y, "mobile_uncertainty");
    },
    drawChartBySid() {

      let _this = this;

      // function addAxesAndLegend (g, xAxis, yAxis, margin, chartWidth, chartHeight) {
      //   var legendWidth  = 200,
      //       legendHeight = 100;

      //   var axes = g.append('g')
      //     .attr('clip-path', 'url(#axes-clip)');

      //   axes.append('g')
      //     .attr('class', 'x axis')
      //     .attr('transform', 'translate(0,' + chartHeight + ')')
      //     .call(xAxis);

      //   axes.append('g')
      //     .attr('class', 'y axis')
      //     .call(yAxis)
      //     .append('text')
      //       .attr('transform', 'rotate(-90)')
      //       .attr('y', 6)
      //       .attr('dy', '.71em')
      //       .style('text-anchor', 'end')
      //       .text('(cpm)');
      // }

      // function drawPaths (g, data, x, y, styleClass) {
      //   var upperInnerArea = d3.area()
      //     .x (function (d) { return x(d.time) || 1; })
      //     .y0(function (d) { return y(d.upper95); })
      //     .y1(function (d) { return y(d.avg); });

      //   var medianLine = d3.line()
      //     .x(function (d) { return x(d.time); })
      //     .y(function (d) { return y(d.avg); });

      //   var lowerInnerArea = d3.area()
      //     .x (function (d) { return x(d.time) || 1; })
      //     .y0(function (d) { return y(d.avg); })
      //     .y1(function (d) { return y(d.lower95); });

      //   g.datum(data);

      //   g.append('path')
      //     .attr('class', 'area upper ' + styleClass)
      //     .attr('d', upperInnerArea)
      //     .attr('clip-path', 'url(#rect-clip)');

      //   g.append('path')
      //     .attr('class', 'area lower ' + styleClass)
      //     .attr('d', lowerInnerArea)
      //     .attr('clip-path', 'url(#rect-clip)');

      //   g.append('path')
      //     .attr('class', 'median-line')
      //     .attr('d', medianLine)
      //     .attr('clip-path', 'url(#rect-clip)');
      // }


      function makeChartBySid (dataList) {
        var margin = { top: 10, right: 20, bottom: 30, left: 35 },
            chartWidth  = _this.svgWidth  - margin.left - margin.right,
            chartHeight = _this.svgHeight - margin.top  - margin.bottom;

        let begin = null, end = null;
        if(_this.timeRange != null) {
          begin = _this.timeRange.begintime;
          end = _this.timeRange.endtime;
        } else {
          begin = _this.defaultTimeRange.begintime;
          end = _this.defaultTimeRange.endtime;
        }

        let max = 0;
        dataList.forEach(data => {
          let tmp = d3.max(data, d => d.upper95);
          if(tmp > max) {
            max = tmp;
          }
        })

        var x = d3.scaleTime().range([0, chartWidth])
                  .domain([new Date(begin), new Date(end)]),
            y = d3.scaleLinear().range([chartHeight, 0])
                  .domain([0, max]);

        var xAxis = d3.axisBottom(x)
                      .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10),//.tickFormat(d => d.getHours()),
            yAxis = d3.axisLeft(y)
                      .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10);

        var g = _this.svg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
        
        let lineStyle = "inner";
        // if(params.category == "static") {
        //   lineStyle = "inner2";
        // }
        
        dataList.forEach(data => {
          _this.drawPaths(g, data, x, y, lineStyle);
        })
      }
      
      /***************************************************************************************/
      
      
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", Object.assign({}, this.timeRange || this.defaultTimeRange, this.sidList[this.sidList.length-1]))
        .then((response) => {
          var data = response.data.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: parseFloat(d.lower95),
              avg: parseFloat(d.avg),
              upper95: parseFloat(d.upper95)
            };
          });
          this.sidDataList.push(data)
          makeChartBySid(this.sidDataList);
        })
    },
    timeRangeUpdated(params) {
      console.log("TrendChart updated...", params);
      this.timeRange = params;
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
      this.drawChart();
    },
    sensorSelected(params) {
      // let newParams = null;
      // if(this.timeRange == null) {
      //   newParams = Object.assign({}, params, this.defaultTimeRange);
      // } else {
      //   newParams = Object.assign({}, params, this.timeRange);
      // }
      
      // console.log(newParams);
      this.sidList.push(params)
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
      this.drawChartBySid();
    }
  }
}
</script>

<style scoped>
.trendchart >>> .axis path, 
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.trendchart >>> .axis text {
  fill: #000;
}

.trendchart >>> .axis .tick line {
  stroke: rgba(0, 0, 0, 0.1);
}

.trendchart >>> .area {
  stroke-width: 1;
}

.trendchart >>> .area.outer, 
.legend .outer {
  fill: rgba(230, 230, 255, 0.8);
  stroke: rgba(216, 216, 255, 0.8);
}

.trendchart >>> .mobile_uncertainty {
  fill: rgba(127, 127, 255, 0.8);
  stroke: rgba(96, 96, 255, 0.8);
}

.trendchart >>> .static_uncertainty {
  fill: rgba(255, 127, 0, 0.8);
  stroke: rgba(255, 127, 0, 0.8);
}

.trendchart >>> .median-line,
.legend .median-line {
  fill: none;
  stroke: #000;
  stroke-width: 1;
}

.trendchart >>> .legend .legend-bg {
  fill: rgba(0, 0, 0, 0.5);
  stroke: rgba(0, 0, 0, 0.5);
  opacity: 0.1;
}


.trendchart >>> .legend text {
  font-size: 10px;
}
</style>
