<template>
  <div class="ban-pick">
    <h1>BanPick</h1>
    <div class="ban-pick-page">
      <div class="section">
        <div class="our-team-section">
          <h3>우리팀</h3>
          <div v-for="(box, index) in our_boxes" :key="box" @click="selectBox(box)" :style="{border: box === selectedBox ? '2px solid red' : ''}" class="lane-box" >
            <img :src="boxImages[index] || emptyBoxImage" alt="빈 상자" class="lane-img"/>
          </div>
        </div>
        <div class="champion-secction">
          <div class="champion-buttons">
            <ChampionButton @select-champion="selectChampion" />
          </div>
          <div>
            <button @click="submit" class="submit">챔피언 선택</button>
          </div>
        </div>
        <div class="opponent-team-section">
          <h3>상대팀</h3>
          <div v-for="(box, index) in opponent_boxes" :key="box" @click="selectBox(box)" :style="{border: box === selectedBox ? '2px solid red' : ''}" class="lane-box">
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
      lanes: [
        { name: '탑', image: require('@/assets/logo.png') },
        { name: '정글', image: require('@/assets/logo.png') },
        { name: '미드', image: require('@/assets/logo.png') },
        { name: '바텀', image: require('@/assets/logo.png') },
        { name: '서폿', image: require('@/assets/logo.png') },
      ],

      laneChampions: { '탑': '', '정글': '', '미드': '', '바텀': '', '서폿': '' },
      opponentLaneChampions: { '탑': '', '정글': '', '미드': '', '바텀': '', '서폿': '' },
    };
  },
  computed: {
  ...mapState('box', ['selectedBox', 'selectedImage', 'boxImages'])
  },
  methods: {
    selectChampion(imageUrl) {
    this.setSelectedImage(imageUrl);
    },
    ...mapMutations('box', ['setSelectedBox', 'setSelectedImage', 'insertImageToBox']),
    selectBox(box) {
      this.setSelectedBox(box)
    },
    submit() {
      if (this.selectedBox && this.selectedImage) {
        this.insertImageToBox();
      } else {
        alert('빈 상자와 이미지를 선택해주세요.')
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
  max-height: 90%;
  background-color: #252e41
}
.ban-pick-page {
  align-items: center;
}

.submit {
  width: 20vw;
  height: 3vw;
  margin-top: 5vh;
}

.section {
  display: flex;
  align-items: flex-start;
  height: 60%;
}
.lane-box {
  margin: 0px;
}

.lane-img {
  height: 100px;
  width: 250px;
  object-fit: cover;
}

.champion-buttons {

  height: 55vh;
  overflow-y: scroll;
  display: block;
  justify-content: center;
}

.champion-secction{
  margin: 5% 0% 0% 1.5%;
  width: 40vw;
}
.our-team-section {
  width: 20%;
  height: 50%;
  display: block;
}

.opponent-team-section {
  width: 20%;
  height: 50%;
  display: block;
}
</style>