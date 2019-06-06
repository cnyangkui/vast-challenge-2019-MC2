<template>
  <div id="app">
    <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
    <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
    <el-row :gutter="3">
      <el-col :span="12">
        <el-row><el-col :span="24"><div class="grid-content left"></div></el-col></el-row>
        <el-row><el-col :span="24"><div class="grid-content left"></div></el-col></el-row>
        <el-row><el-col :span="24"><div class="grid-content left"></div></el-col></el-row>
      </el-col>
      <el-col :span="12">
        <el-row><el-col :span="24"><div class="grid-content bg-purple-dark"><StHimarkmap></StHimarkmap></div></el-col></el-row>
        
      </el-col>
    </el-row>
    
  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
import StHimarkmap from './components/StHimarkMap.vue'
import * as d3 from 'd3'

export default {
  name: 'app',
  components: {
    StHimarkmap
  },
  data() {
    return {
      
    }
  },
  mounted() {
    this.layout();
    this.$nextTick(() => {
      
    })
  },
  methods: {
    layout() {
      let bodyHeight = document.body.clientHeight
      let leftdivs = document.querySelectorAll(".left")
      for(let i=0; i<leftdivs.length; i++) {
        console.log(leftdivs[i].style)
        leftdivs[i].style.minHeight = Math.floor(bodyHeight / 3 - 5) + "px";
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
html, body, #app .el-row, .el-col{
  width: 100%;
  height: 100%;
}
.grid-content {
  border-radius: 4px;
  border: 1px solid black;
}
.el-row {
  margin-bottom: 2px;
}
.el-row last-child {
  margin-bottom: 0;
}
</style>
