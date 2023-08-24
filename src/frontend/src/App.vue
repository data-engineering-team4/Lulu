<template>
  <div id="app">
    <router-view/>
    <div>
      Selected Image: {{ $store.state.selectedImage }}
      <button @click="selectImage(1)">Select Image 1</button>
      <button @click="selectImage(2)">Select Image 2</button>
    </div>
  </div>
</template>

<script>
import { mapMutations } from 'vuex';

export default {
  name: 'App',
  components: {

  },
  methods: {
    ...mapMutations(['selectImage']),
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
