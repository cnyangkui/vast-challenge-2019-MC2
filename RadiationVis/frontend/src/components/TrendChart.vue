<template>
  <div :id="cid">
    <div class="trendchart"></div>
    <div class="mytooltip" ></div>
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
    addX(g, xAxis,margin, chartWidth, chartHeight) {
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
        .text('(cpm)');
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

      // legend.append('rect')
      //   .attr('class', 'legend-bg')
      //   .attr('width',  legendWidth)
      //   .attr('height', legendHeight);

      legend.append('line')
        // .attr('class', 'static_uncertainty')
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
        .text('Average radiation readings and 95 confidence interval of all SSs');

      legend.append('line')
        // .attr('class', 'mobile_uncertainty')
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
        .text('Average radiation readings and 95 confidence interval of all MSs');

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
        .text('Average radiation readings and 95 confidence interval of all SSs');

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
        .text('Average radiation readings and 95 confidence interval of all MSs');

    },
    drawPaths (g, data, x, y, color) {
      let upperInnerArea = d3.area()
        .x (function (d) { return x(d.time) || 1; })
        .y0(function (d) { return y(d.upper95); })
        .y1(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX);

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.time) || 1; })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); })
        .curve(d3.curveMonotoneX);

      g.datum(data);
      let bisectDate = d3.bisector(function(d) { return d.date; }).left;

      g.append('path')
        .attr('d', upperInnerArea)
        .style('fill', color)
        .style('cursor', 'pointer')
        .on('mousemove', mouseover)
        .on('mouseout', mouseout)

      g.append('path')
        .attr('d', lowerInnerArea)
        .style('fill', color)
        .style('cursor', 'pointer')
        .on('mousemove', mouseover)
        .on('mouseout', mouseout)

      g.append('path')
        .attr('d', medianLine)
        .attr('fill', 'none')
        .attr('stroke', color)
        .style('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('mousemove', mouseover)
        .on('mouseout', mouseout)

      let _this = this;
      let mytooltip = d3.select(`#${this.cid} .mytooltip`);
      function mouseover() {
        let x0 = x.invert(d3.mouse(this)[0]);
        let i = bisectDate(data, x0, 1);
        let d0 = data[i - 1], d1 = data[i], 
          d = x0 - d0.date > d1.date - x0 ? d1 : d0;
        let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M")
        mytooltip
            .html(`time: ${timeFormat(d.time)} <br/>average radiation reading: ${d.avg.toFixed(2)}<br/>95% confidence interval: [${d.lower95.toFixed(2)}, ${d.upper95.toFixed(2)}]`)
            .style('left', () => {
              if(d3.event.offsetX + 200 > _this.svgWidth) {
                return (d3.event.offsetX - 200) + 'px'
              } else {
                return (d3.event.offsetX + 5) + 'px'
              }
            })
            .style('top', () => {
              if(d3.event.offsetY + 80 > _this.svgHeight) {
                return (d3.event.offsetY -80 ) + 'px'
              } else {
                return (d3.event.offsetY ) + 'px'
              }
            })
            .style('display', 'inline-block');
      }
      function mouseout() {
        mytooltip.style('display', 'none');
      }
    },
    drawBaseline(g, data, x, y) {
      let baseline = d3.line()
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.value); });
      g.datum(data);
      g.append('path')
        .attr('d', baseline)
        .style('stroke', 'grey')
        .style('stroke-width', 1)
        .style('stroke-dasharray', 5);
    },
    drawTick(g, x, y, max) {
      g.append('text')
        .attr('x', '10px')
        .attr('y', y(14.6))
        .attr('dx', '0em')
        .attr('dy', '1em')
        .attr("font-size",10)
        .attr("font-style", 'italic')
        .attr("fill", '#999')
        .text('background');
      g.append('text')
        .attr('x', '-2')
        .attr('y', y(14.6))
        .attr('dy', '.5em')
        .attr("font-size",10)
        .attr("font-style", 'italic')
        .attr("fill", '#999')
        .style('text-anchor', 'end')
        .text('14.6');
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

      if(end.getTime() - begin.getTime() > 6 * 3600 * 1000) {
        let s = new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours());
        let e = new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours())
        x = d3.scaleTime()
          .range([0, chartWidth])
          .domain([s, e]);
        basedata = [{date: s, value: 14.6}, {date: e, value: 14.6}];
      } else {
        let s = new Date(begin.getFullYear(), begin.getMonth(), begin.getDate(), begin.getHours(), begin.getMinutes());
        let e = new Date(end.getFullYear(), end.getMonth(), end.getDate(), end.getHours(), end.getMinutes());
        x = d3.scaleTime()
          .range([0, chartWidth])
          .domain([s, e]);
        basedata = [{date: s, value: 14.6}, {date: e, value: 14.6}];
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

      let y = d3.scaleLinear().range([chartHeight, 0])
                .domain([12, max]);

      let static_y = d3.scaleLinear().range([chartHeight, 0])
                .domain([13, max]);
      let mobile_y = d3.scaleLinear().range([chartHeight, 0])
                .domain([13, max]);
            

      let xAxis = d3.axisBottom(x)
        .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10);
        // .tickFormat((d, i) => {
        //   var formatMonth = d3.timeFormat("%B %d")
        //   if(d.getHours() %24 == 0) {
        //       return formatMonth(d);
        //     } else {
        //       return `${d.getHours()}:00`
        //     }
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
        this.drawBaseline(g, basedata, x, y);
        this.drawTick(g, x, y);
      } else {
        if(this.checkedItem[0] == 'static') {
         this.addX(g, xAxis, margin, chartWidth, chartHeight);
        this.addY(g, yAxis_static, margin, chartWidth, chartHeight);
          this.addStaticLegend(g);
          this.drawPaths(g, this.originData.data.staticData, x, static_y, "rgba(224, 4, 255, 0.6)");
          this.drawBaseline(g, basedata, x, static_y);
          this.drawTick(g, x, static_y);
        } else {
          this.addX(g, xAxis, margin, chartWidth, chartHeight);
          this.addY(g, yAxis_mobile, margin, chartWidth, chartHeight);
          this.addMobileLegend(g);
          this.drawPaths(g, this.originData.data.mobileData, x, mobile_y, "rgba(54,95,139, 0.6)");
          this.drawBaseline(g, basedata, x, mobile_y);
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
.mytooltip {
	position: absolute;
  display: none;
  min-width: 80px;
  height: auto;
  background    : rgb(229, 226, 226);
  border        : none;
  border-radius : 8px;
  padding: 14px;
  text-align: start;
  font-size: 10px;
}
</style>
