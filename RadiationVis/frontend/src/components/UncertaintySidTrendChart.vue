<template>
  <div :id="cid">
    <div class="control">
      <label style="margin-left:5px;">{{originData.category == 'static' ? 'SS': 'MS'}}-{{originData.sid}}</label>
      <label style="margin-left:10px;">Time: {{originData.timeRange.begintime}} - {{originData.timeRange.endtime}}</label>
      <label style="margin-left:10px;">Inteval: {{interval == 'hour'? 'By 1 hour': 'By 1 minute'}}</label>
      <input class="button" type="button" value="delete" @click="remove();">
      <input class="button" type="button" value="detail" @click="showDetail();">
      <input class="button" type="button" value="position" @click="showGeoInfo();">
    </div>
    <div class="trendchart"></div>
    <div class="mytooltip" ></div>
    <div class="dialog">
      <el-dialog
      :visible.sync="srScatterVisible"
      width="70%">
      <div style="height: 500px;"><SrScatter :cid="scatterCid" :category="originData.category" :sid="originData.sid"></SrScatter></div>
      <span slot="footer" class="dialog-footer">
      </span>
    </el-dialog>
    </div>
  </div>
</template>

<script>
import SrScatter from './SrScatter.vue'
import * as d3 from "d3"
import axios from '../assets/js/http';
export default {
  name: 'TrendChart',
  components: {
    SrScatter,
  },
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
      srScatterVisible: false,
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
      d3.select(`#${this.cid}`).style("position", "relative");
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

        let max = d3.max(this.originData.data, d => d.std);

        let x, y;

        if(end.getTime() - begin.getTime() > 6 * 3600 * 1000) {
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
                      .tickSizeInner(-chartHeight).tickSizeOuter(0).tickPadding(10).ticks(10)
                      .tickFormat((d, i) => {
                        var formatMonth = d3.timeFormat("%B %d")
                        var formatTime = d3.timeFormat("%H:%M")
                        if(d.getHours() %24 == 0) {
                            return formatMonth(d);
                          } else {
                            return formatTime(d);
                          }
                      });
        var yAxis = d3.axisLeft(y)
                      .tickSizeInner(-chartWidth).tickSizeOuter(0).tickPadding(10).ticks(3);
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
        .text('(STD)');
    },
    drawSidPath(g, data, x, y) {
      let medianLine = d3.line()
        .x(function (d) { return x(d.time); })
        .y(function (d) { return y(d.std); })
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
    let bisectDate = d3.bisector(function(d) { return d.time; }).left;
     if(this.componentStyle == 'point') {
        g.append('g')
        .selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', (d, i) => x(d.time))
        .attr('cy', (d, i) => y(d.std))
        .attr('r', 2)
        .style("fill", (d) => {
          if(this.originData.category == 'static') {
            return "rgba(224, 4, 255, 0.6)"
          } else {
            return "rgba(54,95,139, 0.6)";
          }
        })
        .style('cursor', 'pointer')
        .on('mouseover', (d) => {
          let mytooltip = d3.select(`#${this.cid} .mytooltip`);
          let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M")
        mytooltip
            .html(`time: ${timeFormat(d.time)} <br/>average radiation reading: ${d.std.toFixed(2)}`)
            .style('left', () => {
              if(d3.event.offsetX + 200 > _this.svgWidth) {
                return (d3.event.offsetX - 200) + 'px'
              } else {
                return (d3.event.offsetX + 5) + 'px'
              }
            })
            .style('top', () => {
              if(d3.event.offsetY + 50 > _this.svgHeight) {
                return (d3.event.offsetY -50 ) + 'px'
              } else {
                return (d3.event.offsetY ) + 'px'
              }
            })
            .style('display', 'inline-block');
        })
        .on('mouseout', mouseout)

      } else {
        g.append('path')
        .attr('d', medianLine)
        .style('stroke', () => {
          if(this.originData.category == 'static') {
            return "rgba(224, 4, 255, 0.6)"
          } else {
            return "rgba(54,95,139, 0.6)";
          }
        })
        .style('fill', 'none')
        .style('cursor', 'pointer')
        .on('mousemove', mouseover)
        .on('mouseout', mouseout)
      }

      let _this = this;
      let mytooltip = d3.select(`#${this.cid} .mytooltip`);
      function mouseover() {
        let x0 = x.invert(d3.mouse(this)[0]);
        let i = bisectDate(data, x0, 1);
        let d0 = data[i - 1], d1 = data[i], 
          d = x0 - d0.time > d1.time - x0 ? d1 : d0;
        let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M")
        mytooltip
            .html(`time: ${timeFormat(d.time)} <br/>standard deviation: ${d.std.toFixed(2)}`)
            .style('left', () => {
              if(d3.event.offsetX + 150 > _this.svgWidth) {
                return (d3.event.offsetX - 150) + 'px'
              } else {
                return (d3.event.offsetX + 5) + 'px'
              }
            })
            .style('top', () => {
              if(d3.event.offsetY + 50 > _this.svgHeight) {
                return (d3.event.offsetY -50 ) + 'px'
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
    clearAllg() {
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
    },
    showDetail() {
      this.srScatterVisible = !this.srScatterVisible;
    },
    remove() {
      this.$root.eventHub.$emit("removeSidTrendChart", {category: this.originData.category, sid: this.originData.sid});
    },
    showGeoInfo() {
      this.$root.eventHub.$emit("showPosition", {category: this.originData.category, sid: this.originData.sid});
    }
    // timeRangeUpdated(params) {
    //   this.timeRange = params;
    //   console.log(this.timeRange)
    //   d3.select(`#${this.cid} svg`).selectAll('g').remove();
    //   this.drawChartBySid();
    // },
    // sensorSelected(params) {
    //   if(this.sidList.length >= 5) {
    //     this.sidList = [];
    //     this.sidDataList = [];
    //   }
    //   this.sidList.push(params)
    //   d3.select(`#${this.cid} svg`).selectAll('g').remove();
    //   this.drawChartBySid();
    // }
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
    },
    scatterCid: function() {
      return this.cid + '_scatter'
    },
    interval: function() {
      let begin = this.originData.timeRange.begintime || this.defaultTimeRange.begintime;
      let end = this.originData.timeRange.endtime || this.defaultTimeRange.endtime;
      begin = new Date(begin);
      end = new Date(end);
      if(end.getTime() - begin.getTime() > 6 * 3600 * 1000) {
        return 'hour'
      } else {
        return 'minute'
      }
    }
  }
}
</script>

<style scoped>
.dialog >>> .el-dialog__header {
  padding: 0px;
}
.control {
  background-color: #ccc;
  height: 28px;
  font-size: 12px;
}
.control label {
  line-height: 28px;
}
.control .button {
  float: right;
  margin-right: 5px;
  font-size: 12px;
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
  fill: rgba(54,95,139, 0.6);
  stroke: rgba(54,95,139, 0.9);
  opacity: 0.6;
}

.trendchart >>> .static_uncertainty {
  fill: rgba(224, 4, 255, 0.6);
  stroke: rgba(224, 4, 255, 0.9);
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
