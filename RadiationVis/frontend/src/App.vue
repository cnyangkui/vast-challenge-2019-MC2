<template>
  <div id="app">
    <el-row>
      <el-col :span="4" class="left">
        <div class="grid-content">
          <div class="control-container">
            <div class="control-header">
              <label>Overview</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="radio" value="radiation" name="overview-type" v-model="overviewType"><label>radiation</label></div>
                <div class="input-ele"><input type="radio" value="uncertainty" name="overview-type" v-model="overviewType"><label>uncertainty</label></div>
              </div>
            </div>
          </div>
          <div class="control-container">
            <div class="control-header">
              <label>TimeSeries</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static"><label>Static</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile"><label>Mobile</label></div>
              </div>
              <div class="input-ele-group">
                <div class="input-ele"><input type="radio" value="global" name="timeSeriesState"><label>global</label></div>
                <div class="input-ele"><input type="radio" value="local" name="timeSeriesState" disabled><label>local</label></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 5px;">
            <div class="control-header">
              <label>Treemap

              </label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static"><label>Static</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile"><label>Mobile</label></div>
              </div>
              <div class="input-ele-group">
                <div class="input-ele"><input type="button" value="global"></div>
                <div class="input-ele"><input type="button" value="local"></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 5px;">
            <div class="control-header">
              <label>Map</label>
            </div>
            <div class="control-content" v-if="overviewType=='radiation'">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_kriging_check"><label>SI(kriging)</label></div>
                <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_idw_check"><label>SI(idw)</label></div>
                <div class="input-ele"><input type="checkbox" v-model="mapControl.r_mi_idw_check"><label>MI(idw)</label></div>
              </div>
            </div>
            <div class="control-content" v-else-if="overviewType=='uncertainty'">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" v-model="mapControl.u_mi_check"><label>MI(idw)</label></div>
                <div class="input-ele"><input type="checkbox" v-model="mapControl.u_pie_check"><label>Pie</label></div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="20" class="right">
        <el-row class="right_top">
          <el-col :span="24">
            <div class="grid-content">
              <time-series-chart :cid="`time_series_chart_container`"></time-series-chart>
            </div>
          </el-col>
        </el-row>
        <el-row class="right_bottom">
          <el-col :span="10" class="bottom_left">
            <div class="grid-content bottom_left_top">
              <treemap :cid="`treemap-container`"></treemap>
            </div>
            <div class="grid-content bottom_left_bottom">
              <div class="innerdiv">
                <trend-chart :cid="`trend_chart_container`"></trend-chart>
              </div>
              <div v-for="(item, index) in trendCharts" :key='index' class="innerdiv">
                <sid-trend-chart :cid="`trend_chart_container_${index}`" :originData="item"></sid-trend-chart>
                <!-- {{item}} -->
              </div>
            </div>
          </el-col>
          <el-col :span="14" class="bottom_right">
            <div class="grid-content">
              <openlayers :mapControl="mapControl"></openlayers>
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
import SidTrendChart from './components/SidTrendChart.vue'
// import PackageChart from './components/PackageChart.vue'
// import SimilarityScatter from './components/SimilarityScatter'
import * as d3 from 'd3'
import axios from './assets/js/http'

export default {
  name: 'app',
  components: {
    Openlayers,
    SrScatter,
    TrendChart,
    TimeSeriesChart,
    Treemap,
    SidTrendChart
    // PackageChart,
    // SimilarityScatter
  },
  data() {
    return {
      srScatterVisible: false,
      overviewType: "radiation",
      mapControl: {
        r_si_kriging_check: false,
        r_si_idw_check: false,
        r_mi_idw_check: false,
        r_s_check: false,
        r_m_check: false,
        t_heatmap_check: false,
        u_pie_check: false,
        u_mi_check: false,
      },
      items: [
        { message: 'Foo' },
        { message: 'Bar' }
      ],
      trendCharts: [],
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
    }
  },
  created: function () {
    this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
     this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
   },
  mounted() {
    // this.layout();
    this.$nextTick(() => {
      
    })
  },
  methods: {
    sensorSelected(params) {
      // 如果该传感器已经存在，则不添加
      if(this.trendCharts.filter(d => d.category==params.category && d.sid==params.sid).length > 0) {
        return;
      }
      this.getTrendChartData(params);
    },
    getTrendChartData(params) {
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", params)
        .then((response) => {
          let data = response.data.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: parseFloat(d.lower95),
              avg: parseFloat(d.avg),
              upper95: parseFloat(d.upper95)
            };
          });
          let trendChart = {
            category: params.category,
            sid: params.sid,
            timeRange: {begintime: params.begintime, endtime: params.endtime},
            data: data
          }
          this.trendCharts.push(trendChart);
      })
    },
    timeRangeUpdated(params) {
      for(let i=0, length=this.trendCharts.length; i<length; i++) {
        this.trendCharts.pop();
      }
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
.control-container {
  font-size: 12px;
}
.control-header {
  background-color: #ccc;
  height: 28px;
}
.control-header input {
  line-height: 28px;
  margin-left: 5px;
}
.control-header label {
  line-height: 28px;
  margin-left: 5px;
}
.control-container .input-ele-group {
  width: 90%;
  margin-left: 5%;
}
.control-container .input-ele {
  width: 50%;
  display: inline-block;
}
input :disabled {
  background-color: rgb(235, 235, 228);
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
  overflow-y: auto;
  overflow-x: hidden;
}
.bottom_left_bottom .innerdiv {
  height: 100%;
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
