<template>
  <div id="app">
    <el-row :gutter=1>
      <el-col :span="4" class="left">
        <div class="grid-content">
          <div class="control-container">
            <div class="control-header">
              <label>Data Center</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele">
                  <input type="checkbox" value="radiation" name="overview-type" v-model="datatype"><label>Radiation</label>
                </div>
                <div class="input-ele">
                  <input type="checkbox" value="uncertainty" name="overview-type" v-model="datatype"><label>Uncertainty</label>
                  </div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>All Sensor Temporal View Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static"  v-model="timeSeriesCheckedState"><label>SS</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile" v-model="timeSeriesCheckedState"><label>MS</label></div>
              </div>
              <div class="input-ele-group">
                <div class="input-ele"><input type="radio" value="global" name="timeSeriesState" v-model="timeSeriesControl.state"><label>Global</label></div>
                <div class="input-ele"><input type="radio" value="local" name="timeSeriesState" v-model="timeSeriesControl.state" :disabled="timeSeriesControl.localDisabled"><label>Local</label></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>Treemap View Settings</label>
            </div>
            <div class="control-content">
              <div class="input-ele-group">
                <div class="input-ele"><input type="checkbox" value="static" v-model="treemapCheckedState"><label>SS</label></div>
                <div class="input-ele"><input type="checkbox" value="mobile" v-model="treemapCheckedState"><label>MS</label></div>
              </div>
              <div class="input-ele-group">
                <div class="input-ele" style="margin-top: 6px;"><input type="button" value="Back" @click="getTreemap1();"></div>
              </div>
            </div>
          </div>
          <div class="control-container" style="margin-top: 10px;">
            <div class="control-header">
              <label>Gis View Settings</label>
            </div>
            <div class="input-ele-group">
              <div class="input-ele"><input type="checkbox" v-model="mapControl.icon_s_check"><label>SS</label>
              <img :src="require('./assets/img/static.png')" alt="" width="20px;"></div>
              <div class="input-ele"><input type="checkbox" v-model="mapControl.icon_m_check"><label>MS</label>
              <img :src="require('./assets/img/mobile.png')" alt="" width="20px;"></div>
              <!-- <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_idw_check"><label>SI(idw)</label></div> -->
              <!-- <div class="input-ele"><input type="checkbox" v-model="mapControl.point_s"><label>MI(idw)</label></div> -->
            </div>
            <div class="input-ele-group">
              <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_idw_check"><label>SI</label></div>
              <!-- <div class="input-ele"><input type="checkbox" v-model="mapControl.r_si_idw_check"><label>SI(idw)</label></div> -->
              <div class="input-ele"><input type="checkbox" v-model="mapControl.r_mi_idw_check"><label>MI</label></div>
            </div>
            <div class="input-ele-group">
              <div class="input-ele"><input type="checkbox" v-model="mapControl.u_mi_check"><label>uncertainty(MI)</label></div>
              <div class="input-ele"><input type="checkbox" v-model="mapControl.u_pie_check"><label>Pie</label></div>
            </div>
            <div class="input-ele-group">
            </div>
          </div>
          <div class="control-container">
            <div class="control-header">
              <label>Uncertainty Settings</label>
            </div>
            <div class="control-content">
              <div class="uncertainty-container">
                <div><label>Uncertainty index system</label></div>
                <ul>
                  <li>U1: Inconsistency</li>
                  <li>U2: Credibility</li>
                  <li>U3: Precision</li>
                  <li>U4: Data completeness</li>
                </ul>
                <div><label>Uncertainty levels</label></div>
                <ul>
                  <li>Level 1: <img :src="require('./assets/img/star.png')" alt="" width="20px;">low</li>
                  <li>Level 2: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    guarded
                  </li>
                  <li>Level 3: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    elevated
                  </li>
                  <li>Level 4: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    high
                  </li>
                  <li>Level 5: 
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    <img :src="require('./assets/img/star.png')" alt="" width="20px;">
                    severe
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="20" class="right">
        <el-row class="right_top">
          <el-col :span="24">
            <div class="grid-content" v-if="datatype.length == 2">
              <time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></time-series-chart>
              <trend-chart v-show="timeSeriesControl.state=='local'" :cid="`trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></trend-chart>
            </div>
            <div class="grid-content" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <radiation-time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`radiation_time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></radiation-time-series-chart>
              <radiation-trend-chart v-show="timeSeriesControl.state=='local'" :cid="`radiation_trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></radiation-trend-chart>
            </div>
            <div class="grid-content" v-if="datatype.length == 1 && datatype[0] == 'uncertainty'">
              <uncertainty-time-series-chart v-show="timeSeriesControl.state=='global'" :cid="`uncertainty_time_series_chart_container`" :checkedItem="timeSeriesCheckedState"></uncertainty-time-series-chart>
              <uncertainty-trend-chart v-show="timeSeriesControl.state=='local'" :cid="`uncertainty_trend_local_chart_container`" :originData="trendChart" :checkedItem="timeSeriesCheckedState"></uncertainty-trend-chart>
            </div>
          </el-col>
        </el-row>
        <el-row class="right_bottom">
          <el-col :span="10" class="bottom_left">
            <div class="grid-content bottom_left_top" v-if="datatype.length == 2">
              <treemap v-show="treemapState=='treemap1'" :cid="`treemap-container`" :originData="treemap1"></treemap>
              <treemap v-show="treemapState=='treemap2'" :cid="`treemap-container2`" :originData="treemap2"></treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <radiation-treemap v-show="treemapState=='treemap1'" :cid="`radiation-treemap-container`" :originData="treemap1"></radiation-treemap>
              <radiation-treemap v-show="treemapState=='treemap2'" :cid="`radiation-treemap-container2`" :originData="treemap2"></radiation-treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 1 && datatype[0]=='uncertainty'">
              <uncertainty-treemap v-show="treemapState=='treemap1'" :cid="`uncertainty-treemap-container`" :originData="treemap1"></uncertainty-treemap>
              <uncertainty-treemap v-show="treemapState=='treemap2'" :cid="`uncertainty-treemap-container2`" :originData="treemap2"></uncertainty-treemap>
            </div>
            <div class="grid-content bottom_left_top" v-if="datatype.length == 0">
              
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 2">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <sid-trend-chart :cid="`trend_chart_container_${index}`" :originData="item"></sid-trend-chart>
              </div>
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 1 && datatype[0]=='radiation'">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <radiation-sid-trend-chart :cid="`radiation_trend_chart_container_${index}`" :originData="item"></radiation-sid-trend-chart>
              </div>
            </div>
            <div class="grid-content bottom_left_bottom" v-if="datatype.length == 1 && datatype[0]=='uncertainty'">
              <div v-for="(item, index) in sidTrendCharts" :key='index' class="innerdiv">
                <uncertainty-sid-trend-chart :cid="`uncertainty_trend_chart_container_${index}`" :originData="item"></uncertainty-sid-trend-chart>
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
import TimeSeriesChart from './components/TimeSeriesChart.vue'
import RadiationTimeSeriesChart from './components/RadiationTimeSeriesChart.vue'
import UncertaintyTimeSeriesChart from './components/UncertaintyTimeSeriesChart.vue'
import TrendChart from './components/TrendChart.vue'
import RadiationTrendChart from './components/RadiationTrendChart.vue'
import UncertaintyTrendChart from './components/UncertaintyTrendChart.vue'
import Treemap from './components/Treemap.vue'
import UncertaintyTreemap from './components/UncertaintyTreemap.vue'
import RadiationTreemap from './components/RadiationTreemap.vue'
import SidTrendChart from './components/SidTrendChart.vue'
import RadiationSidTrendChart from './components/RadiationSidTrendChart.vue'
import UncertaintySidTrendChart from './components/UncertaintySidTrendChart.vue'
// import PackageChart from './components/PackageChart.vue'
// import SimilarityScatter from './components/SimilarityScatter'
import * as d3 from 'd3'
import axios from './assets/js/http'

export default {
  name: 'app',
  components: {
    Openlayers,
    SrScatter,
    TimeSeriesChart,
    RadiationTimeSeriesChart,
    UncertaintyTimeSeriesChart,
    TrendChart,
    RadiationTrendChart,
    UncertaintyTrendChart,
    Treemap,
    RadiationTreemap,
    UncertaintyTreemap,
    SidTrendChart,
    RadiationSidTrendChart,
    UncertaintySidTrendChart
    // PackageChart,
    // SimilarityScatter
  },
  data() {
    return {
      srScatterVisible: false,
      datatype: ["radiation", "uncertainty"],
      timeSeriesControl: {
        state: 'global',
        localDisabled: true,
      },
      timeSeriesCheckedState: ['static', 'mobile'],
      treemapCheckedState: ['static', 'mobile'],
      treemapState: 'treemap1',
      mapControl: {
        r_si_kriging_check: false,
        r_si_idw_check: false,
        r_mi_idw_check: false,
        r_s_check: false,
        icon_m_check: false,
        icon_s_check: false,
        t_heatmap_check: false,
        u_pie_check: false,
        u_mi_check: false,
        playState: false,
      },
      trendChart: null,
      sidTrendCharts: [],
      treemap1: null,
      treemap2: null,
      timeRange: null,
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
              upper95: 1.96 * d.standarderror + d.avg,
              std: d.std
            };
          });
          var mobile_data = data.mobile.map(function (d) {
            return {
              time:  parseDate(d.time),
              lower95: -1.96 * d.standarderror + d.avg,
              avg: d.avg,
              upper95: 1.96 * d.standarderror + d.avg,
              std:d.std
            };
          });
          this.trendChart = {
            timeRange: params,
            data: {staticData: static_data, mobileData: mobile_data}
          }
        })

    },
    getTreemapDataByTimeRange(params) {
      if(this.treemapCheckedState.length == 2) {
        axios.post("/calSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState
          }
        })
      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'static') {
        axios.post("/calStaticSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState
          }
        })

      }
      if(this.treemapCheckedState.length == 1 && this.treemapCheckedState[0] == 'mobile') {
        axios.post("/calMobileSensorClusters/", params).then(response => {
          this.treemap1 = {
            state: this.treemapState,
            data: response.data,
            timeRange: params,
            checkedState: this.treemapCheckedState
          }
        })

      }
      
    },
    getTreemap1() {
      this.treemapState = 'treemap1';
    },
    getTreemap2(params) {
      this.treemapState = 'treemap2';
      // d3.csv('static/data/final_outlier_pattern.csv')
      this.treemap2 = {
        state: this.treemapState,
        data: params,
        timeRange: this.timeRange,
        checkedState: this.treemapCheckedState
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
  },
  watch: {
    treemapCheckedState(n, o) {
      console.log(n)
      this.getTreemapDataByTimeRange(this.timeRange);
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
  border: 1px solid #ccc;
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
  font-size: 18px;
  margin-left: 5px;
}
.control-container .input-ele-group {
  width: 92%;
  margin-left: 4%;
  height: 30px;
}
.control-container .input-ele {
  width: 50%;
  display: inline-block;
}
.control-content label {
  line-height: 30px;
}
.uncertainty-container {
  margin-left: 5px;
}
.uncertainty-container div{
  height: 30px;
}
/* .uncertainty-container li {
  height: 0px;
  list-style-type: circle;
} */
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
