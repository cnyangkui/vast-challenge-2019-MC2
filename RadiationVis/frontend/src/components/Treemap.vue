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
    }
  },
  created: function () {
      this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
      this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
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
    drawChart() {
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

      axios.post("/calSensorClusters/", this.timeRange || this.defaultTimeRange).then(response => {

        let data = response.data;
        
        var root = d3.hierarchy(data)
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
              if(this.sidList.length > 3) {
                this.sidList = [];
                alert("最多三个...")
              }
              this.sidList.push({category: category, sid: sid});
              this.$root.eventHub.$emit("sensorSelected", {category: category, sid: sid});
            })

        cell.append("rect")
            .attr("id", function(d) { return d.data.id; })
            .attr("width", function(d) { return d.x1 - d.x0; })
            .attr("height", function(d) { return d.y1 - d.y0; })
            .attr("fill", function(d) { return color(d.parent.data.id); });

        cell.append("clipPath")
            .attr("id", function(d) { return "clip-" + d.data.id; })
          .append("use")
            .attr("xlink:href", function(d) { return "#" + d.data.id; });

        cell.append("text")
            .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
          .selectAll(".treemap tspan")
            .data(function(d) { return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
          .enter().append("tspan")
            .attr("x", 4)
            .attr("y", function(d, i) { return 13 + i * 10; })
            .text(function(d) { return d; })
            .style("font-size", 8);

        cell.append("title")
            .text(function(d) { return d.data.id + "\n" + format(d.value); });

      });
    },
    timeRangeUpdated(params) {
      console.log("Treemap updated")
      this.timeRange = params;
      d3.select(`#${this.cid} svg`).selectAll('g').remove();
      this.drawChart();
    }
  }
}
</script>

<style scoped>
.package >>> .label {
  font-size: 8px;
}
</style>
