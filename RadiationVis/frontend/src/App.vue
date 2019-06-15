<template>
  <div id="app">
    <el-row :gutter="3">
      <el-col :span="10">
        <el-row class="left1">
          <el-col :span="24">
            <div class="grid-content">
              <div class="nav">
                TimeRange: {{}}
                <el-button type="text" @click="timeAxisVisible = true">点击打开 Dialog</el-button>
              </div>
              <div class="main">
                <TrendChart cid="trend_chart_container"></TrendChart>
              </div>
            </div>
          </el-col>
        </el-row>
        <el-row class="left2">
          <el-col :span="12">
            <div class="grid-content">
              <SimilarityScatter cid="similarity_scatter_container"></SimilarityScatter>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="grid-content">
              <!-- <SimilarityScatter cid="similarity_scatter_container2"></SimilarityScatter> -->
            </div>
          </el-col>
        </el-row>
        <el-row class="left3">
          <el-col :span="24">
            <div class="grid-content">
              <el-button type="text" @click="dialogVisible = true">点击打开 Dialog</el-button>
            </div>
          </el-col>
        </el-row>
      </el-col>
      <el-col :span="13">
        <el-row class="right"><el-col :span="24"><div class="grid-content"><Openlayers></Openlayers></div></el-col></el-row>
      </el-col>
    </el-row>
    <el-dialog
      title="提示"
      :visible.sync="timeAxisVisible"
      width="70%">
      <div style="height: 300px;"><TrendChartWithTimeBrush cid="trend_chart_container2"></TrendChartWithTimeBrush></div>
      <div style="height: 300px;"><TrendChart cid="trend_chart_container3"></TrendChart></div>
      <span slot="footer" class="dialog-footer">
      </span>
    </el-dialog>
    <el-dialog
      title="提示"
      :visible.sync="dialogVisible"
      width="70%">
      <div style="height: 300px;"><SRScatter cid="SR_scatter_container"></SRScatter></div>
      <span slot="footer" class="dialog-footer">
      </span>
    </el-dialog>
  </div>
</template>

<script>
import SRScatter from './components/SRScatter.vue'
import SimilarityScatter from './components/SimilarityScatter.vue'
import Openlayers from './components/Openlayers.vue'
import TrendChart from './components/TrendChart.vue'
import TrendChartWithTimeBrush from './components/TrendChartWithTimeBrush.vue'
import * as d3 from 'd3'

export default {
  name: 'app',
  components: {
    Openlayers,
    SRScatter,
    SimilarityScatter,
    TrendChart,
    TrendChartWithTimeBrush
  },
  data() {
    return {
      timeAxisVisible: false,
      dialogVisible: false,
    }
  },
  mounted() {
    // this.layout();
    this.$nextTick(() => {
      
    })
  },
  methods: {
    layout() {
      let bodyHeight = document.body.clientHeight
      let leftdivs = document.querySelectorAll(".left")
      for(let i=0; i<leftdivs.length; i++) {
        leftdivs[i].style.height = Math.floor(bodyHeight / 3 - 8) + "px";
      }
      document.querySelector(".right").style.minHeight = (bodyHeight -8 )+ "px";
    },
    handleClose(done) {
      done();
    }
  }
}
</script>

<style>
/* #app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */

* {
  padding:0;
  margin:0;
}
html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
.el-row {
  display: block; 
  margin-bottom: 5px;
}
.el-row last-child {
  margin-bottom: 0;
}
.el-col {
  height: 100%;
}
.grid-content {
  border-radius: 4px;
  border: 1px solid black;
  height: 100%;
}
.left1, .left2, .left3 {
  height: 230px;
}
.right {
  height: 700px;
}
.nav {
  height: 10%;
  font-size: 10px;
}
.main {
  height: 90%;
}
</style>
