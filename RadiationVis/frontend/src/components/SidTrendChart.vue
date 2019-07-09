<template>
  <div :id="cid">
    <div class="control">
      <label>{{originData.category == 'static' ? 'SS': 'MS'}}: {{originData.sid}}</label>
      <!-- <input class="button" type="button" value="delete"> -->
    </div>
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
    componentStyle: String
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
      timeRange: null,
      sid: null,
      category: null,
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
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
      this.drawChartBySid();
    },
    selfAdaptionSvgSize() {
      let parentNode = document.querySelector(`#${this.cid}`).parentNode;
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight - document.querySelector(`#${this.cid} .control`).clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .trendchart`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    // params: {begintime: xxx, endtime: xxx}
    drawChartBySid() {

      var margin = { top: 10, right: 20, bottom: 30, left: 35 },
            chartWidth  = this.svgWidth  - margin.left - margin.right,
            chartHeight = this.svgHeight - margin.top  - margin.bottom;

        let begin = null, end = null;
        if(this.originData.timeRange != null) {
          begin = new Date(this.originData.timeRange.begintime);
          end = new Date(this.originData.timeRange.endtime);
        } else {
          begin = new Date(this.defaultTimeRange.begintime);
          end = new Date(this.defaultTimeRange.endtime);
        }
        
        let max = d3.max(this.originData.data, d => d.upper95);

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


        var xAxis = d3.axisBottom(x)
                      .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10),//.tickFormat(d => d.getHours()),
            yAxis = d3.axisLeft(y)
                      .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10).ticks(5);

        var g = this.svg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        this.addAxes(g, xAxis, yAxis, margin, chartWidth, chartHeight);
        
        let color = d3.scaleOrdinal(d3.schemeCategory10);

        this.drawSidPath(g, this.originData.data, x, y);
      
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
    drawSidPath(g, data, x, y) {
      let upperInnerArea = d3.area()
        .x (function (d) { return x(d.time); })
        .y0(function (d) { return y(d.upper95); })
        .y1(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX)
        // .defined((d, i, data) => {
        //   if(i == 0) {
        //     return true;
        //   } else {
        //     if(data[i].time.getTime() - data[i-1].time.getTime() <= 3600 * 1000) {
        //       return true;
        //     } else {
        //       return false;
        //     }
        //   }
        // });

      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.avg); })
        .curve(d3.curveMonotoneX)
        // .defined((d, i, data) => {
        //   if(i == 0) {
        //     return true;
        //   } else {
        //     if(data[i].time.getTime() - data[i-1].time.getTime() <= 3600 * 1000) {
        //       return true;
        //     } else {
        //       return false;
        //     }
        //   }
        // });

      let lowerInnerArea = d3.area()
        .x (function (d) { return x(d.time); })
        .y0(function (d) { return y(d.avg); })
        .y1(function (d) { return y(d.lower95); })
        .curve(d3.curveMonotoneX)
        // .defined((d, i, data) => {
        //   if(i == 0) {
        //     return true;
        //   } else {
        //     if(data[i].time.getTime() - data[i-1].time.getTime() <= 3600 * 1000) {
        //       return true;
        //     } else {
        //       return false;
        //     }
        //   }
        // });

      g.datum(data);
      
      if(this.componentStyle == 'point') {
        g.append('g')
        .selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', (d, i) => x(d.time))
        .attr('cy', (d, i) => y(d.avg))
        .attr('r', 2)
        .style("fill", (d) => {
          if(this.originData.category == 'static') {
            return "rgba(224, 4, 255, 0.8)"
          } else {
            return "rgba(54,95,139, 0.8)";
          }
        })

      } else {
        g.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine);
      }

      

      g.append('path')
        .attr('d', upperInnerArea)
        .style('fill', (d) =>{
        if (this.originData.category =='static')
            return "#e004ff"
        else
            return "#41709e"
        })
        .style("opacity", 0.5)
        .style('stroke', (d) => {
        if (this.originData.category =='static')
            return "#9e08b3"
        else
            return "#385e8a"
        });

      g.append('path')
        .attr('d', lowerInnerArea)
        .style('fill', (d) => {
        if (this.originData.category =='static')
            return "#e004ff"
        else
            return "#41709e"
        })
        .style("opacity", 0.5)
        .style('stroke', (d) => {
        if (this.originData.category =='static')
            return "#9e08b3"
        else
            return "#385e8a"
        });

    },
    clearAllg() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
    }
  },
  watch: {
    componentStyle(n, o) {
      this.clearAllg();
      this.drawChartBySid();
    }
  },
  computed: {
    mean: function() {
      if(this.originData) {
        return Math.round(d3.mean(this.originData.data, d => d.avg))
      }
      return null;
    },
    std: function() {
      if(this.originData) {
        return Math.round(d3.mean(this.originData.data, d => d.std), 2)
      }
      return null;
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
