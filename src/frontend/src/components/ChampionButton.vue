<template>
  <div class="champion-buttons-container">
    <div v-for="(image, index) in images" :key="index" class="champion-button" :style="{border: index === selectedChampionIndex ? '3px solid red' : ''}">
      <img :src="image" @click="changeImage(index)" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
  selectedChampionIndex: {
    type: Number,
    required: true
    }
  },
  name: 'ChampionButton',
  data() {
    return {
      champions: {},
      specialImage: 'https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/Rumble.png',
      selectedImage: [],
      images: []
    };
  },
  methods: {
    changeImage(index) {
      this.$emit('select-champion', this.images[index], index);
    },
  },
  mounted() {
    fetch('/champions.json')
      .then(response => response.json())
      .then(data => {
        this.champions = data;
        this.images = Object.values(this.champions).map(name => `https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/${name}.png`);
        this.selectedImage = this.images.map(() => false);
      });
  },
};
</script>

<style>
.champion-buttons-container {
  display: flex;
  flex-wrap: wrap;
  margin-left: 5%;
}
.champion-button {
  width: 6%;
  height: 6%;
  display: inline-block;
  flex-basis: 11.5%;
  margin: 0% 1% 0% 1%;
}
.champion-button img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
