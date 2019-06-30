<template>
  <div :id="cid">
    <div class="package"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import axios from '../assets/js/http'
export default {
  name: 'packageChart',
  props: {
    cid: String
  },
  data() {
    return {
      svg: null,
      svgWidth: null,
      svgHeight: null,
      timeRange: {
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
      this.svg = d3.select(`#${this.cid} .package`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawChart() {
      let margin = 5;

      let diameter = d3.min([this.svgWidth, this.svgHeight]) ;

      let g = this.svg.append("g").attr("transform", "translate(" + (this.svgWidth/2) + "," + (this.svgHeight/2) + ")");

      var color = d3.scaleLinear()
          .domain([-1, 5])
          .range(["hsl(152,80%,80%)", "hsl(228,30%,40%)"])
          .interpolate(d3.interpolateHcl);

      var pack = d3.pack()
          .size([this.svgWidth, this.svgHeight])
          .padding(2);

      axios.post("/calSensorClusters/", this.timeRange).then(response => {

        let root = response.data;
        
        root = d3.hierarchy(root)
            .sum(function(d) { return d.mean; })
            .sort(function(a, b) { return b.value - a.value; });

        var focus = root,
            nodes = pack(root).descendants(),
            view;

        var circle = g.selectAll("circle")
          .data(nodes)
          .enter().append("circle")
            .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
            // .style("fill", function(d) {console.log(d); return d.children ? color(d.depth) : null; })
            .style("fill", function(d) {
              if (d.children) {
                return color(d.depth);
              } else {
                return d.data.name.startsWith('m') ? 'steelblue': 'orange';
              } 
            })
            .style("cursor", "pointer")
            .on("dblclick", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); })
            .on("click", (d, i) => {
              let category = null;
              let sid = null;
              if(d.data.name.startsWith("m")) {
                category = "mobile";
              } else {
                category = "static";
              }
              sid = parseInt(d.data.name.substring(1, d.data.name.length));
              // if(this.sidList.length > 3) {
              //   this.sidList = [];
              //   alert("最多三个...")
              // }
              this.sidList.push({category: category, sid: sid});
              this.$root.eventHub.$emit("sensorSelected", {category: category, sid: sid});
            });

        var text = g.selectAll("text")
          .data(nodes)
          .enter().append("text")
            .attr("class", "label")
            .attr("dx", "-.45em")
            .attr("dy", ".5em")
            // .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
            // .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
            .text(function(d) { 
              if(!d.children){
                return d.data.name.substring(1, d.data.name.length);
              }
             })
             .style("cursor", "pointer")
             .on("click", (d, i) => {
              let category = null;
              let sid = null;
              if(d.data.name.startsWith("m")) {
                category = "mobile";
              } else {
                category = "static";
              }
              sid = parseInt(d.data.name.substring(1, d.data.name.length));
              // if(this.sidList.length > 3) {
              //   this.sidList = [];
              //   alert("最多三个...")
              // }
              this.sidList.push({category: category, sid: sid});
              this.$root.eventHub.$emit("sensorSelected", {category: category, sid: sid});
            });

        var node = g.selectAll("circle,text");

        this.svg
            .on("dblclick", function() { zoom(root); });

        zoomTo([root.x, root.y, root.r * 2 + margin]);

        function zoom(d) {
          var focus0 = focus; focus = d;

          var transition = d3.transition()
              .duration(d3.event.altKey ? 7500 : 750)
              .tween("zoom", function(d) {
                var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                return function(t) { zoomTo(i(t)); };
              });

          // transition.selectAll("text")
          //   .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
          //     .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
          //     .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
          //     .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });
        }

        function zoomTo(v) {
          var k = diameter / v[2]; view = v;
          node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
          circle.attr("r", function(d) { return d.r * k; });
        }
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
