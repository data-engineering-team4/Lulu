<template>
  <div>
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
      specialImage: 'https://ddragon.leagueoflegends.com/cdn/10.6.1/img/champion/Rumble.png',
      selectedImage: [],
      images: []
    };
  },
  methods: {
    changeImage(index) {
      this.selectedImage[index] = !this.selectedImage[index];
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
.champion-button {
  width: 100px; /* 원하는 크기 */
  height: 100px;
  display: inline-block;
}
.champion-button img {
  width: 100%;
  height: 100%;
}
</style>
