<template>
  <div id="app">
    <el-row>
      <el-col :span="4" class="left">
        <div class="grid-content">
          <div>
            <div>
              <div><el-radio v-model="radio" label="radiation" :border="true" size="mini" style="width: 112px;">radiation</el-radio></div>
              <div><el-radio v-model="radio" label="uncertainty" :border="true" size="mini" style="width: 112px;">uncertainty</el-radio></div>
            </div>
            <div v-if="radio=='radiation'">
              <div><el-checkbox :border="true" size="mini" v-model="layerCheckbox.r_si_kriging_check">SI(kriging)</el-checkbox></div>
              <div><el-checkbox :border="true" size="mini" v-model="layerCheckbox.r_si_idw_check">SI(idw)</el-checkbox></div>
              <div><el-checkbox :border="true" size="mini" v-model="layerCheckbox.r_mi_idw_check">MI(idw)</el-checkbox></div>
            </div>
            <div v-else-if="radio=='uncertainty'">
              <div><el-checkbox :border="true" size="mini" v-model="layerCheckbox.u_mi_check">MI(idw)</el-checkbox></div>
              <div><el-checkbox :border="true" size="mini" v-model="layerCheckbox.u_pie_check">Pie</el-checkbox></div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="20" class="right">
        <el-row class="right_top">
          <el-col :span="24">
            <div class="grid-content">
              <time-series-chart cid="time_series_chart_container"></time-series-chart>
            </div>
          </el-col>
        </el-row>
        <el-row class="right_bottom">
          <el-col :span="10" class="bottom_left">
            <div class="grid-content bottom_left_top">
              <treemap cid="treemap-container"></treemap>
            </div>
            <div class="grid-content bottom_left_bottom">
              <trend-chart cid="trend_chart_container"></trend-chart>
            </div>
          </el-col>
          <el-col :span="14" class="bottom_right">
            <div class="grid-content">
              <openlayers :layerCheckbox="layerCheckbox"></openlayers>
            </div>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
    <el-dialog
      :visible.sync="srScatterVisible"
      width="70%">
      <div style="height: 400px;"><sr-scatter cid="Sr_scatter_container"></sr-scatter></div>
      <span slot="footer" class="dialog-footer">
      </span>
    </el-dialog>
  </div>
</template>

<script>
import SrScatter from './components/SrScatter.vue'
import Openlayers from './components/Openlayers.vue'
import TrendChart from './components/TrendChart.vue'
import TimeSeriesChart from './components/TimeSeriesChart.vue'
import Treemap from './components/Treemap.vue'
// import PackageChart from './components/PackageChart.vue'
// import SimilarityScatter from './components/SimilarityScatter'
import * as d3 from 'd3'

export default {
  name: 'app',
  components: {
    Openlayers,
    SrScatter,
    TrendChart,
    TimeSeriesChart,
    Treemap,
    // PackageChart,
    // SimilarityScatter
  },
  data() {
    return {
      srScatterVisible: false,
      radio: "radiation",
      layerCheckbox: {
        r_si_kriging_check: false,
        r_si_idw_check: false,
        r_mi_idw_check: false,
        r_s_check: false,
        r_m_check: false,
        t_heatmap_check: false,
        u_pie_check: false,
        u_mi_check: false,
      }
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
/* .el-row {
  display: block; 
  margin-bottom: 5px;
}
.el-row last-child {
  margin-bottom: 0;
} */
.el-row {
  height: 100%;
}
.el-col {
  height: 100%;
}
.grid-content {
  /* border-radius: 4px; */
  border: 1px solid black;
  height: 100%;
}
.left, .right {
  height: 100%;
}
.right_top {
  height: 16%;
}
.right_bottom {
  height: 84%;
}
.bottom_left, .bottom_right {
  height: 100%;
}
.bottom_left_top {
  height: 60%;
}
.bottom_left_bottom {
  height: 40%;
}
.nav {
  height: 10%;
  font-size: 10px;
}
.main {
  height: 90%;
}
/* .border {
  border-radius: 4px;
  border: 1px solid black;
} */
</style>
