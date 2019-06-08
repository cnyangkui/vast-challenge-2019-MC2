<template>
  <div id="scatterContainer">
    <div id="scatterControl">
      <span>SendorId: {{sid}}</span> &nbsp;
      <el-input size="mini" v-model="minInput" placeholder="min"></el-input> &nbsp;<span>-</span>&nbsp;
      <el-input size="mini" v-model="maxInput" placeholder="max"></el-input>
    </div>
    <div id="scatterContainer">
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import axios from 'axios'
export default {
  name: 'HelloWorld',
  // props: {
  //   msg: String
  // }
  data() {
    return {
      minInput: 0,
      maxInput: 100,
      minValue: null,
      maxValue: null,
      svgWidth: 0,
      svgHeight: 0,
      sid: 1,
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.selfAdaptionSvgSize();
      this.drawSvg();
      this.drawScatter(this.sid)
    })
  },
  methods: {
    selfAdaptionSvgSize() {
      let parentNode = document.getElementById("scatterContainer").parentNode;
      let parentHeight = parentNode.clientHeight;
      let control = document.getElementById("scatterControl");
      this.width = control.clientWidth;
      this.height = parentHeight - control.clientHeight;
    },
    drawSvg() {
      this.svg = d3.select("#scatterContainer").append("svg")
        .attr("width", this.width)
        .attr("height", this.height);
    },
    drawScatter(sid) {
      axios.post("http://localhost:8000/testdb/", {
        sid: this.sid,
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
/* #scatterContainer {
  position: absolute;
} */
.el-input {
  width: 60px;
}
span {
  font-size: 12px;
}
</style>
