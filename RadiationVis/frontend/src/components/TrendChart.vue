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
    cid: String,
    originData: {
      type: Object,
      default: function() {
        return null;
      }
    },
    checkedItem: Array,
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
    }
  },
  created: function () {
      // this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      // this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
      // this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      // this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
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
        this.drawChart();
      }
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector(`#${this.cid}`).parentNode;
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .trendchart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    clearAllg() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
    },
    // params: {begintime: xxx, endtime: xxx}
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
          legendHeight = 45,
          rectWidth = 20,
          rectHeight = 10;

      let legendMargin = {left: 5, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', -10)');

      legend.append('rect')
        .attr('class', 'legend-bg')
        .attr('width',  legendWidth)
        .attr('height', legendHeight);

      legend.append('rect')
        .attr('class', 'mobile_uncertainty')
        .attr('width',  rectWidth)
        .attr('height', rectHeight)
        .attr('x', legendMargin.left)
        .attr('y', legendMargin.top);

      legend.append('text')
        .attr('x', legendMargin.left + rectWidth)
        .attr('y', legendMargin.top)
        .attr('dx', '.5em')
        .attr('dy', '1em')
        .text('mobile');

      legend.append('rect')
        .attr('class', 'static_uncertainty')
        .attr('width',  rectWidth)
        .attr('height', rectHeight)
        .attr('x', legendMargin.left)
        .attr('y', legendMargin.top + rectHeight * 2);

      legend.append('text')
        .attr('x', legendMargin.left + rectWidth)
        .attr('y', legendMargin.top + rectHeight * 2)
        .attr('dx', '.5em')
        .attr('dy', '1em')
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
        .y1(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.time); })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); })
        .curve(d3.curveMonotoneX);

      g.datum(data);

      g.append('path')
        .attr('class', 'area upper ' + styleClass)
        .attr('d', upperInnerArea);

      g.append('path')
        .attr('class', 'area lower ' + styleClass)
        .attr('d', lowerInnerArea);

      g.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine);
    },
    drawBaseline(g, data, x, y) {
      let baseline = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.value); });
      g.datum(data);
      g.append('path')
        .attr('d', baseline)
        .style('stroke', 'grey')
        .style('stroke-width', 1);
    },
    drawChart() {
      let _this = this;

      let margin = { top: 10, right: 5, bottom: 30, left: 30 },
          chartWidth  = _this.svgWidth  - margin.left - margin.right,
          chartHeight = _this.svgHeight - margin.top  - margin.bottom;

      let begin = null, end = null;
      begin = new Date(this.originData.timeRange.begintime);
      end = new Date(this.originData.timeRange.endtime);
     
      let x, y;
      let basedata;

      if(end.getTime() - begin.getTime() > 12 * 3600 * 1000) {
        let s = new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours());
        let e = new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours())
        x = d3.scaleTime()
          .range([0, chartWidth])
          .domain([s, e]);
        basedata = [{date: s, value: 15}, {date: e, value: 15}];
      } else {
        let s = new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours(), begin.getMinutes());
        let e = new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours(), end.getMinutes());
        x = d3.scaleTime()
          .range([0, chartWidth])
          .domain([s, e]);
        basedata = [{date: s, value: 15}, {date: e, value: 15}];
      }

      let max1 = d3.max(this.originData.data.staticData, d => d.upper95);
      let max2 = d3.max(this.originData.data.mobileData, d => d.upper95);
      let max;
      if(this.checkedItem.length == 2) {
        max = max1 > max2 ? max1: max2;
      } else {
        if(this.checkedItem[0] == 'static') {
          max = max1;
        } else if(this.checkedItem[0] == 'mobile') {
          max = max2;
        }
      }

      y = d3.scaleLinear().range([chartHeight, 0])
            .domain([0, max]);

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

      if(this.checkedItem.length == 2) {
        _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
        _this.addLegend(g, chartWidth);
        _this.drawPaths(g, this.originData.data.staticData, x, y, "static_uncertainty");
        _this.drawPaths(g, this.originData.data.mobileData, x, y, "mobile_uncertainty");
        _this.drawBaseline(g, basedata, x, y);
      } else {
        if(this.checkedItem[0] == 'static') {
          _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
          _this.drawPaths(g, this.originData.data.staticData, x, y, "static_uncertainty");
          _this.drawBaseline(g, basedata, x, y);
        } else {
          _this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
          _this.drawPaths(g, this.originData.data.mobileData, x, y, "mobile_uncertainty");
          _this.drawBaseline(g, basedata, x, y);
        }
      }
    },
  },
  watch: {
    originData: {
      handler(n, o) {
        this.clearAllg();
        console.log(n)
        if(n && this.checkedItem.length!=0) {
          this.drawChart();
        }
      },
      deep: true
    },
    checkedItem: function(n, o) {
      this.clearAllg();
      if(n.length != 0 && this.originData) {
        this.drawChart();
      }
    }
  }
}
</script>

<style scoped>
.control {
  background-color: #ccc;
  height: 28px;
  font-size: 12px;
}
.control label {
  line-height: 28px;
}
.control .button {
  border-radius: 5px;
  float: right;
  margin-right: 5px;
  margin-top: 2px;
}
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
  opacity: 0.6;
}

.trendchart >>> .static_uncertainty {
  fill: rgba(255,182,193, 0.8);
  stroke: rgba(255,182,193, 0.8);
  opacity: 0.6;
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
