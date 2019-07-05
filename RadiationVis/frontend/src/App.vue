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
                <div class="input-ele">
                  <input type="radio" value="radiation" name="overview-type" v-model="overviewType"><label>radiation</label>
                  <!-- <el-radio v-model="overviewType" label="radiation">radiation</el-radio> -->
                </div>
                <div class="input-ele">
                  <input type="radio" value="uncertainty" name="overview-type" v-model="overviewType"><label>uncertainty</label>
                  <!-- <el-radio v-model="overviewType" label="uncertainty">uncertainty</el-radio> -->
                  </div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>TimeSeries</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static"  v-model="timeSeriesCheckedState"><label>Static</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile" v-model="timeSeriesCheckedState"><label>Mobile</label></div>
              </div>
              <div class="input-ele-group">
                <div class="input-ele"><input type="radio" value="global" name="timeSeriesState" v-model="timeSeriesControl.state"><label>global</label></div>
                <div class="input-ele"><input type="radio" value="local" name="timeSeriesState" v-model="timeSeriesControl.state" :disabled="timeSeriesControl.localDisabled"><label>local</label></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>Treemap</label>
            </div>
            <div class="control-content">
              <!-- <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static"><label>Static</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile"><label>Mobile</label></div>
              </div> -->
              <div class="input-ele-group">
                <div class="input-ele"><input type="button" value="返回" @click="getTreemap1();"></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>Map</label>
            </div>
            <div class="control-content" v-show="overviewType=='radiation'">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_kriging_check"><label>SI(kriging)</label></div>
                <!-- <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_idw_check"><label>SI(idw)</label></div> -->
                <div class="input-ele"><input type="checkbox" v-model="mapControl.r_mi_idw_check"><label>MI(idw)</label></div>
              </div>
            </div>
            <div class="control-content" v-show="overviewType=='uncertainty'">
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
              <time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></time-series-chart>
              <trend-chart v-show="timeSeriesControl.state=='local'" :cid="`trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></trend-chart>
            </div>
          </el-col>
        </el-row>
        <el-row class="right_bottom">
          <el-col :span="10" class="bottom_left">
            <div class="grid-content bottom_left_top">
              <treemap v-show="treemapState=='treemap1'" :cid="`treemap-container`" :originData="treemap1"></treemap>
              <treemap v-show="treemapState=='treemap2'" :cid="`treemap-container2`" :originData="treemap2"></treemap>
            </div>
            <div class="grid-content bottom_left_bottom">
              <!-- <div class="innerdiv">
                <trend-chart :cid="`trend_chart_container`"></trend-chart>
              </div> -->
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
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
      timeSeriesControl: {
        state: 'global',
        localDisabled: true,
      },
      timeSeriesCheckedState: ['static', 'mobile'],
      treemapState: 'treemap1',
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
      trendChart: null,
      sidTrendCharts: [],
      treemap1: null,
      treemap2: null,
      defaultTimeRange: {
        begintime: '2020-04-06 00:00:00',
        endtime: '2020-04-11 00:00:00'
      },
    }
  },
  created: function () {
    this.$root.eventHub.$on('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$on('sensorSelected', this.sensorSelected);
      this.$root.eventHub.$on('getTreemap2', this.getTreemap2);
   },
   // 最好在组件销毁前
   // 清除事件监听
   beforeDestroy: function () {
     this.$root.eventHub.$off('timeRangeUpdated', this.timeRangeUpdated);
      this.$root.eventHub.$off('sensorSelected', this.sensorSelected);
      this.$root.eventHub.$off('getTreemap2', this.getTreemap2);
   },
  mounted() {
    // this.layout();
    this.$nextTick(() => {
      this.getTreemapDataByTimeRange(this.defaultTimeRange);
    })
  },
  methods: {
    sensorSelected(params) {
      // 如果该传感器已经存在，则不添加
      if(this.sidTrendCharts.filter(d => d.category==params.category && d.sid==params.sid).length > 0) {
        return;
      }
      this.getSidTrendChartData(params);
    },
    getSidTrendChartData(params) {
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeriesBySid/", params)
        .then((response) => {
          let data = response.data.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg,
              std: d.std
            };
          });
          let sidtrendChart = {
            category: params.category,
            sid: params.sid,
            timeRange: {begintime: params.begintime, endtime: params.endtime},
            data: data
          }
          this.sidTrendCharts.push(sidtrendChart);
      })
    },
    getTrendChartDataByTimeRange(params) {
      let parseDate = d3.timeParse('%Y-%m-%d %H:%M:%S');
      axios.post("/calTimeSeries/", params)
        .then((response) => {
          let data = response.data;
          var static_data = data.static.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg
            };
          });
          var mobile_data = data.mobile.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg
            };
          });
          this.trendChart = {
            timeRange: params,
            data: {staticData: static_data, mobileData: mobile_data}
          }
        })

    },
    getTreemapDataByTimeRange(params) {
      axios.post("/calSensorClusters/", params).then(response => {
        this.treemap1 = {
          state: this.treemapState,
          data: response.data,
          timeRange: params
        }
      })
    },
    getTreemap1() {
      this.treemapState = 'treemap1';
    },
    getTreemap2(params) {
      this.treemapState = 'treemap2';
      this.treemap2 = {
        state: this.treemapState,
        data: params,
        timeRange: this.timeRange
      }
    },
    timeRangeUpdated(params) {
      this.timeRange = params;
      this.sidTrendCharts = [];
      if(params) {
        this.timeSeriesControl.localDisabled = false;
        // this.timeSeriesControl.state = "local";
        this.trendChart = null;
        this.getTrendChartDataByTimeRange(params);
        this.treemap1 = null;
        this.treemap2 = null;
        this.treemapState = 'treemap1';
        this.getTreemapDataByTimeRange(params);
      }  else {
        this.timeSeriesControl.localDisabled = true;
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
  font-size: 15px;
}
.control-header {
  background-color: #ccc;
  height: 45px;
}
.control-header label {
  line-height: 45px;
  margin-left: 5px;
  font-size: 18px;
}
.control-container .input-ele-group {
  width: 92%;
  margin-left: 4%;
  height: 40px;
}
.control-container .input-ele {
  width: 50%;
  display: inline-block;
}
.control-container label {
  line-height: 40px;
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
  height: 50%;
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
