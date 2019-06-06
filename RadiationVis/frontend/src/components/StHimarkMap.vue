<template>
  <div id="mapContainer">
    <div id="heatmap">
      <img ref="geomap" :src="himarkmap.imageSrc">
    </div>
  </div>
</template>

<script>
import CityMap from "../../public/static/js/citymap";
import * as d3 from "d3"
import * as h337 from "heatmap.js"
export default {
  name: 'StHimarkMap',
  props: {
    // msg: String
  },
  data() {
    return {
      himarkmap: new CityMap(),
      svg: null,
    }
  },
  created() {
    console.log(this.himarkmap)
  },
  mounted() {
    this.$nextTick(() => {
      // dom虽然加载完成,但是图片资源的请求不一定已经返回
      this.$refs.geomap.addEventListener('load', () => {
        this.loadMap();
      })
    })
  },
  methods: {
    loadMap() {
      this.selfAdaptionSize();
      this.drawSvg();
      this.drawStaticSensor();
      this.drawHeatmap();
      
    },
    selfAdaptionSize() {
      let width = d3.select("#mapContainer").style("width").replace("px", "");
      this.$refs.geomap.width = parseFloat(width);
      let height = this.$refs.geomap.offsetHeight;
      this.himarkmap.setMapSize(width, height);
    },
    drawSvg() {
      this.svg = d3.select("#mapContainer").append("svg")
        .attr("width", this.himarkmap.width)
        .attr("height", this.himarkmap.height)
        .style("position", "absolute")
        .style("top", 0)
        .style("left", 0)
    },
    drawStaticSensor() {
      d3.csv("static/data/StaticSensorLocations.csv", (d) => {
        let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
        this.svg.append("circle")
          .attr("id", "sid_" + d.sid)
          .attr("cx", coordinate[0])
          .attr("cy", coordinate[1])
          .attr("r", 3)
          .attr("fill", 'steelblue');
      })
    },
    drawHeatmap() {
      this.heatmap = d3.select("#heatmap")
        .style("width", this.himarkmap.width + "px")
        .style("height", this.himarkmap.height + "px")
        .style("position", "absolute")
        .style("top", 0)
        .style("left", 0)

      let heatmapInstance = h337.create({
        // only container is required, the rest will be defaults
        container: document.querySelector('#heatmap')
      });

      d3.csv("static/data/StaticSensorReadingsExample.csv").then(csvdata => {
        let points = [];
        csvdata.forEach(d => {
          let coordinate = this.himarkmap.mappingToCoordinate(parseFloat(d.lat), parseFloat(d.long));
          points.push({"x": Math.round(coordinate[0]), "y": Math.round(coordinate[1]), 'value': parseFloat(d.value), "radius": 80});
        })
        let data = {"max": 20, "data": points};
        console.log(data)
        heatmapInstance.setData(data);
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#mapContainer {
  position: relative;
}
</style>
