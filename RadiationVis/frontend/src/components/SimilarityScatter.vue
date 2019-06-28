<template>
  <div :id=cid>
    <div class="scatter">
    </div>
    <div class="tooltip"></div>
  </div>
</template>

<script>
import axios from '../assets/js/http'
import * as d3 from "d3"
export default {
  name: 'SimilarityScatter',
  props: {
    cid: String
  },
  data() {
    return {
      svg: null,
      svgWidth: 0,
      svgHeight: 0,
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
      this.drawScatter();
    },
    selfAdaptionSvgSize() {
      let container = document.querySelector(`#${this.cid}`);
      let parentNode = container.parentNode;
      this.svgWidth = parentNode.clientWidth;
      this.svgHeight = parentNode.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select(`#${this.cid} .scatter`).append("svg")
        .attr("width", this.svgWidth)
        .attr("height", this.svgHeight);
    },
    drawScatter(params) {
      let margin = {top: 10, right: 10, bottom: 10, left: 10};
      let width = this.svgWidth - margin.left - margin.right;
      let height = this.svgHeight - margin.top - margin.bottom;
      let g = this.svg.append("g")
        .attr('transform', `translate(${margin.left}, ${margin.top})`);
        // .attr
      // let voronoi = d3.voronoi()
      //   .extent([[0, 0], [width, height]]);
        
      let tooltip = document.querySelector(`#${this.cid} .tooltip`);

      // d3.csv("/static/data/SensorSimilarity.csv").then(csvdata => {
      axios.post("/calSensorSimilarity/", params || {begintime: '2020-04-06 00:00:00', endtime: '2020-04-11 00:00:00'})
        .then((response) => {
        let csvdata = response.data;
       
        let xExtent = d3.extent(csvdata, d => parseFloat(d.x))
        let yExtent = d3.extent(csvdata, d => parseFloat(d.y))
        xExtent = [Math.floor(xExtent[0]), Math.ceil(xExtent[1])];
        yExtent = [Math.floor(yExtent[0]), Math.ceil(yExtent[1])];
        
        // Init Scales
        let x = d3.scaleLinear().domain(xExtent).range([0, width]);
        let y = d3.scaleLinear().domain(yExtent).range([height, 0]);


        let points = csvdata.map(d => {
          return [x(parseFloat(d.x)), x(parseFloat(d.y))];
        })
        // g.selectAll("path")
        //   .data(voronoi(points).polygons())
        //   .enter()
        //   .append("path")
        //   .style('stroke', 'tomato')
        //   .style('fill', 'none')
        //   .attr("d", d =>  { 
        //     return d ? "M" + d.join("L") + "Z" : null; 
        //   })  
        g.selectAll(`#${this.cid} .sensor_node`)
          .data(csvdata)
          .enter()
          .append("circle")
          .attr("class", d => `sensor_node ${d.id}`)
          .attr("cx", d => {
            return x(d.x)
          })
          .attr("cy", d => {
            return y(d.y)
          })
          .attr("r", d => {
            let r = Math.sqrt(d.mean / Math.PI);
            return r;
          })
          .attr("fill", d => {
            return d.id.startsWith('m') ? 'steelblue': 'orange';
          })
          .style("opacity", d => {

          })
          // .on("mouseover", (d, i) => {
          //   tooltip.style.display = 'block';
          //   let transl = 'translate(' + (x(d.x)) + 'px, ' + (y(d.y) + 15) + 'px)';
          //   tooltip.style.webkitTransform = transl;
          //   tooltip.innerHTML = d.id;
          // })
          // .on("mouseout", (d, i) => {
          //   tooltip.style.display = 'none';
          // })

          g.selectAll(`#${this.cid} .sensor_text`)
            .data(csvdata)
            .enter()
            .append("text")
            .attr("class", "sensor_text")
            .attr("x", d => {
              return x(d.x)
            })
            .attr("y", d => {
              return y(d.y)
            })
            .attr("dx", "-.5em")
            .attr("dy", ".5em")
            .text(d => d.id.substring(1, d.id.length))
            .style("font-size", 8)
            // .on("mouseover", (d, i) => {
            //   tooltip.style.display = 'block';
            //   let transl = 'translate(' + (x(d.x)) + 'px, ' + (y(d.y) + 15) + 'px)';
            //   tooltip.style.webkitTransform = transl;
            //   tooltip.innerHTML = d.id;
            // })
            // .on("mouseout", (d, i) => {
            //   tooltip.style.display = 'none';
            // });
      })
    },
    timeRangeUpdated(params) {
      d3.select(`#${this.cid} svg g`).remove();
      this.drawScatter(params);
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.selected {
  fill: orange;
}
.tooltip {
  position: absolute;
  left: 0;
  top: 0;
  background: rgba(0,0,0,.8);
  color: white;
  font-size: 14px;
  padding: 5px;
  line-height: 18px;
  display: none;
}
</style>
