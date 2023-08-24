<template>
  <div class="ban-pick">
    <h1 style="color: beige">BanPick</h1>
    <div class="ban-pick-page">
      <div class="section">
        <div class="our-team-section">
          <h2 style="color: #4896ea;">우리팀</h2>
          <div v-for="(box, index) in our_boxes" :key="box" @click="selectBox(box)" :style="{border: box === selectedBox ? '6px solid red' : ''}" class="lane-box" >
            <img :src="boxImages[index] || emptyBoxImage" alt="빈 상자" class="lane-img"/>
          </div>
        </div>
        <div class="champion-secction">
          <div class="champion-buttons">
            <ChampionButton :selectedChampions="selectedChampions" @select-champion="selectChampion" :selectedChampionIndex="selectedChampionIndex"/>
          </div>
          <div>
            <button @click="submit" class="submit" :class="{ 'enabled': isSubmitEnabled }" :disabled="!isSubmitEnabled">챔피언 선택</button>
          </div>
        </div>
        <div class="opponent-team-section">
          <h2 style="color: #ea494c;">상대팀</h2>
          <div v-for="(box, index) in opponent_boxes" :key="box" @click="selectBox(box)" :style="{border: box === selectedBox ? '6px solid red' : ''}" class="lane-box">
            <img :src="boxImages[index+5] || emptyBoxImage" alt="빈 상자" class="lane-img"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChampionButton from '@/components/ChampionButton.vue';
import { mapState, mapMutations } from 'vuex'

export default {
  name: 'BanPickPage',
  components: {
    ChampionButton,
  },
  data() {
    return {
      our_boxes: [1, 2, 3, 4, 5],
      opponent_boxes: [6, 7, 8, 9, 10],
      emptyBoxImage: require('@/assets/black.png'),
      // selectedChampions: Array(164).fill(false),
      selectedChampionIndex: null,
    };
  },
  computed: {
    ...mapState('box', ['selectedBox', 'selectedImage', 'boxImages']),
    isSubmitEnabled() {
      return this.selectedBox && this.selectedImage;
    }
  },
  methods: {
    selectChampion(imageUrl, index) {
      this.selectedChampionIndex = index;
      this.setSelectedImage(imageUrl);
       // console.log('Selected Champion Index:', this.selectedChampionIndex); // 로그 출력
      // this.selectedChampions[index+2] = true;
    },
    ...mapMutations('box', ['setSelectedBox', 'setSelectedImage', 'insertImageToBox']),
    selectBox(box) {
      this.setSelectedBox(box)
    },
    submit() {
      if (this.selectedBox && this.selectedImage) {
        this.insertImageToBox();
        // this.selectedChampions = null;
      } else {
        alert('?!!!')
      }
    }
  },
};
</script>
<style>
.ban-pick {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #252e41
}

.ban-pick-page {
  align-items: center;
}

.section {
  display: flex;
  align-items: flex-start;
  height: 80%;
}

.champion-secction{
  margin: 10% 2% 0% 0%;
  width: 40vw;
}

.our-team-section {
  width: 20%;
  height: 80%;
  display: block;
}

.opponent-team-section {
  width: 20%;
  height: 100%;
  display: block;
}
.submit {
  width: 15vw;
  height: 3vw;
  margin-top: 5vh;
  font-size: x-large;
  background-color: #ccc;
}
.submit.enabled {
  background-color: #4896ea;
}

.lane-box {
  height: 100%;
  width: 100%;
  margin: 0px;
  object-fit: fill;
}

.lane-img {
  height: 40%;
  width: 100%;
  object-fit: fill;
}

.champion-buttons {
  height: 55vh;
  overflow-y: scroll;
  display: block;
  justify-content: center;
}

</style>