<template>
  <div class="champion-buttons-container">
    <div v-for="(image, index) in images" :key="index" class="champion-button">
      <img :src="selectedImage[index] ? specialImage : image" @click="changeImage(index)" />
    </div>
  </div>
</template>

<script>
export default {
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
      this.selectedImage[index] = !this.selectedImage[index];
      if (this.selectedImage[index]) {
      this.$emit('select-champion', this.images[index]);
      }
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
}
.champion-button {
  width: 5%;
  height: 5%;
  display: inline-block;
  flex-basis: 14.2%;
}
.champion-button img {
  width: 90%;
  height: 90%;
}
</style>
