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
    addX(g, xAxis, margin, chartWidth, chartHeight) {
      g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);
      d3.selectAll("g.x-axis g.tick line")//选中所有g下类别为tick
        .attr("y2",(d) => {
          if(d.getHours() %24 == 0) {
              return 6;
            } else {
              return 4
            }
        })
        .style("stroke-width",(d) => {
          if(d.getHours() %24 == 0) {
              return 1.3;
            } else {
              return 1
            }
        });
    },
    addY(g, yAxis, margin, chartWidth, chartHeight) {
      g.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('(STD)');
    },
    addLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(224, 4, 255, 0.6)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all SSs');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span * 3)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span * 3)
        .style('stroke', 'rgba(54,95,139,0.5)')
        .style('stroke-width', 2);

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span * 3)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all MSs');

    },
    addStaticLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(224, 4, 255, 0.6)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all SSs');

    },
    addMobileLegend (g) {
      let legendWidth  = 70,
          legendHeight = 45,
          lineWidth = 30,
          span = 10;

      let legendMargin = {left: 25, top: 5, right: 5, bottom: 5};

      let legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(0, -5)');

      legend.append('line')
        .attr('x1', legendMargin.left)
        .attr('y1', legendMargin.top + span)
        .attr('x2', legendMargin.left + lineWidth)
        .attr('y2', legendMargin.top + span)
        .style('stroke', 'rgba(54,95,139,0.5)')
        .style('stroke-width', 2);
        

      legend.append('text')
        .attr('x', legendMargin.left + lineWidth)
        .attr('y', legendMargin.top + span)
        .attr('dx', '.5em')
        .attr('dy', '.4em')
        .text('Standard deviation of all MSs');

    },
    drawPaths (g, data, x, y, color) {

      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.std); })
        .curve(d3.curveMonotoneX);

      g.datum(data);

      g.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine)
        // .style('fill', color)
        .style('stroke', color)
        .style('stroke-width', 2);
    },
    drawTick(g, x, y, max) {
      let domain = y.domain();
      g.append('text')
        .attr('x', '-2')
        .attr('y', y(domain[0]))
        .attr('dy', '.5em')
        .attr("font-size",10)
        .style('text-anchor', 'end')
        .text(domain[0]);
      g.append('text')
        .attr('x', '-2')
        .attr('y', y(domain[1]))
        .attr('dy', '.5em')
        .attr("font-size",10)
        .style('text-anchor', 'end')
        .text(Math.round(max || domain[1]));
      
    },
    drawChart() {

      let margin = { top: 10, right: 5, bottom: 30, left: 30 },
          chartWidth  = this.svgWidth  - margin.left - margin.right,
          chartHeight = this.svgHeight - margin.top  - margin.bottom;

      let begin = null, end = null;
      begin = new Date(this.originData.timeRange.begintime);
      end = new Date(this.originData.timeRange.endtime);
     
      let x;
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

      let max1 = d3.max(this.originData.data.staticData, d => d.std);
      let max2 = d3.max(this.originData.data.mobileData, d => d.std);
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

      let y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, max]);

      let static_y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, max]);
      let mobile_y = d3.scaleLinear().range([chartHeight, 0])
                .domain([0, max]);


      let xAxis = d3.axisBottom(x)
        .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10);
        // .tickFormat((d, i) => {
        //   if(i % 2 == 0) {
        //     if(i == 0 || static_data[i].date.getDate() != static_data[i-1].date.getDate()) {
        //       return `${d.getMonth()+1}/${d.getDate()}`;
        //     } else {
        //       return `${d.getHours()}`
        //     }
        //   }
        // }),
      let yAxis = d3.axisLeft(y)
        .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);
      let yAxis_static = d3.axisLeft(static_y)
        .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);
      let yAxis_mobile = d3.axisLeft(mobile_y)
        .tickSizeInner(0).tickSizeOuter(0).tickPadding(10).ticks(0);

      let g = this.svg.append('g')
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      if(this.checkedItem.length == 2) {
       this.addX(g, xAxis, margin, chartWidth, chartHeight);
        this.addY(g, yAxis, margin, chartWidth, chartHeight);
        this.addLegend(g);
        this.drawPaths(g, this.originData.data.staticData, x, y, "rgba(224, 4, 255, 0.6)");
        this.drawPaths(g, this.originData.data.mobileData, x, y, "rgba(54,95,139, 0.5)");
        this.drawTick(g, x, y);
      } else {
        if(this.checkedItem[0] == 'static') {
          this.addX(g, xAxis, margin, chartWidth, chartHeight);
          this.addY(g, yAxis_static, margin, chartWidth, chartHeight);
          this.addStaticLegend(g);
         this.drawPaths(g, this.originData.data.staticData, x, static_y, "rgba(224, 4, 255, 0.6)");
          this.drawTick(g, x, static_y);
        } else {
          this.addX(g, xAxis, margin, chartWidth, chartHeight);
          this.addY(g, yAxis_mobile, margin, chartWidth, chartHeight);
          this.addMobileLegend(g);
          this.drawPaths(g, this.originData.data.mobileData, x, mobile_y, "rgba(54,95,139, 0.5)");
          this.drawTick(g, x, mobile_y);
        }
      }
    },
  },
  watch: {
    originData: {
      handler(n, o) {
        this.clearAllg();
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
  fill: #41709e;
  stroke:  #385e8a;
  opacity: 0.6;
}

.trendchart >>> .static_uncertainty {
  fill: #e004ff;
  stroke: #9e08b3;
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
