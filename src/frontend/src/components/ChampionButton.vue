<template>
  <div class="champion-buttons-container">
    <div v-for="(image, index) in images" :key="index" class="champion-button" :class="{ disabled: disabledChampions.includes(index) }" :style="{border: index === selectedChampionIndex ? '8px solid #6438af' : ''}">
      <img :src="image" @click="changeImage(index)" style="  max-width: 80%;max-height: 80%;" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
  selectedChampionIndex: {
      type: Number,
      required: true
    },
    disabledChampions: {
      type: Array,
      default: () => []
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
      if (this.disabledChampions.includes(index)) return;
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
  margin-left: 2%;
  justify-content: center;

}
.champion-button {
  justify-content: center;
  align-items: center;
  display: flex;
  flex-basis: 15%;
  margin: 1% 3% 3% 1%;
  border-radius: 10px;
  max-width: 20%;
  width: 8vw;
  height: 8vh;
  background: #eeeeee;
  box-shadow:  5px 5px 3px #b7b7b7,
               -5px -5px 3px #ffffff;
  cursor: pointer;
}
.champion-button.disabled {
  filter: grayscale(100%);
  pointer-events: none;
}
.champion-button img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 20px;

}
</style>
