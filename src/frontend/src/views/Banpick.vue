<template>
  <div class="ban-pick">
    <div class="ban-pick-page">
      <div class="ban-pick-board">
        <div class="title-section">
         <div class="custom-light-font" style="display: inline-block;">BanPick&nbsp;</div>
         <div class="custom-font" style="display: inline-block;">DashBoard</div>
        </div>
        <div class="section">
          <div class="left-section">
          추천해줄곳 or 밴
          </div>
          <div class="main-section">
            <div class="our-team-section" @mousedown="selectOurTeam" @mouseup="unselectTeams" @mouseleave="unselectTeams">
            <h2 :style="{ color: ourTeamSelected ? '#4c00ff' : '#b899ff' }" :class="[ourTeamSelected ? 'custom-font' : 'custom-light-font', 'custom-font']">우리팀</h2>
          <div v-for="(box, index) in our_boxes" :key="box" @click="selectBox(box)" :class="['our-lane-box', box === selectedBox ? 'selected' : '', 'our-neumorphism-style'] ">
            <img v-if="boxImages[index]" :src="boxImages[index]" alt="Champion Image" class="lane-img"/>
          </div>
        </div>
        <div class="champion-secction">
          <h1 class="custom-font" style="color: #9752ff;">챔피언을 선택하세요!</h1>
          <div class="champion-buttons">
            <ChampionButton :selectedChampionIndex="selectedChampionIndex" :disabledChampions="disabledChampions" @select-champion="selectChampion"/>
          </div>
          <div>
            <button @click="submit" class="submit neumorphism-style" :class="{ 'enabled': isSubmitEnabled }" :disabled="!isSubmitEnabled">챔피언 선택</button>
          </div>
        </div>
        <div class="opponent-team-section" @mousedown="selectOpponentTeam" @mouseup="unselectTeams" @mouseleave="unselectTeams">
          <h2 :style="{ color: opponentTeamSelected ? '#ff0066' : '#ffadce' }" :class="[opponentTeamSelected ? 'custom-font' : 'custom-light-font', 'custom-font']">상대팀</h2>
          <div v-for="(box, index) in opponent_boxes" :key="box" @click="selectBox(box)" :class="['opponent-lane-box', box === selectedBox ? 'selected' : '', 'opponent-neumorphism-style']">
            <img v-if="boxImages[index+5]" :src="boxImages[index+5]" alt="Champion Image" class="lane-img"/>
          </div>
        </div>
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
      ourTeamSelected: false,
      opponentTeamSelected: false,
      our_boxes: [1, 2, 3, 4, 5],
      opponent_boxes: [6, 7, 8, 9, 10],
      selectedChampionIndex: null,
      boxImages: Array(10).fill(null),
      disabledChampions: [],
    };
  },
  computed: {
    ...mapState('box', ['selectedBox', 'selectedImage']),
    isSubmitEnabled() {
      return this.selectedBox && this.selectedImage;
    }
  },
  methods: {
    selectChampion(imageUrl, index) {
      if (this.disabledChampions.includes(index)) return;
      this.selectedChampionIndex = index;
      this.setSelectedImage(imageUrl);
    },
    ...mapMutations('box', ['setSelectedBox', 'setSelectedImage']),
    selectBox(box) {
      this.setSelectedBox(box)
    },
    selectOurTeam() {
      this.ourTeamSelected = true;
      this.opponentTeamSelected = false;
    },
    selectOpponentTeam() {
      this.ourTeamSelected = false;
      this.opponentTeamSelected = true;
    },
    unselectTeams() {
      this.ourTeamSelected = false;
      this.opponentTeamSelected = false;
    },
    submit() {
      if (this.selectedBox && this.selectedImage) {
        this.boxImages[this.selectedBox - 1] = this.selectedImage;
        this.setSelectedBox(null);
        this.setSelectedImage(null);
        this.disabledChampions.push(this.selectedChampionIndex);
        this.selectedChampionIndex = null;
      } else {
        alert('?!!!')
      }
    }
  },
};
</script>
<style scoped>
@import "@/assets/css/fonts.css";
.custom-font {
  font-family: 'Doctum Bold', sans-serif;
}
.custom-light-font {
  font-family: 'Doctum Light', sans-serif;
}
</style>

<style>
.ban-pick {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #9752ff
}

.ban-pick-page {
  margin-top: 3%;
  align-items: center;
  width: 80%;
  height: 100%;
}

.ban-pick-board{
  height: 90%;
  border-radius: 20px;
  background: #eeeeee;
  box-shadow:  20px 20px 10px #6438af,
               -1px -1px 2px #ffffff;
}
.title-section {
  display: block;
  text-align: left;
  padding: 2% 0% 0% 3%;
  font-size: 30px;
  font-weight: 500;
  color: #9752ff;
}

.section {
  display: flex;
  align-items: flex-start;
  margin: 2%;
  }
.left-section{
  display: flex;
  width: 10vw;
  height: 10vh;
  //background-color: black;
}
.main-section{
  display: flex;
  align-items: flex-start;
  width: 60vw;
  margin-left: 10%;
  margin-right: 2%;
  margin-bottom: 4%;
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}
.champion-secction{
  margin: 1% 3% 3% 1%;
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
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}
.submit.enabled {
  background-color: #4896ea;
}

.our-lane-box {
  height: 10vh;
  width: 6vw;
  margin: 5% 0px 0% 20%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.our-lane-box.selected {
  border: 5px solid blue;
}

.opponent-lane-box {
  height: 10vh;
  width: 6vw;
  margin: 5% 20% 0% 0%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.opponent-lane-box.selected {
  border: 5px solid red;
}

.lane-img {
  height: 40%;
  width: 100%;
  object-fit: contain;
  border-radius: 20px;
}

.champion-buttons {
  height: 40vh;
  overflow-y: scroll;
  display: block;
  justify-content: center;
  padding: 3% 0% 3% 0%;
  width: 40vw;
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}

.our-neumorphism-style:active {
  box-shadow: inset 5px 5px 10px #d1d1d1, inset -5px -5px 10px #ffffff;
  border: 2px solid blue;
}

.opponent-neumorphism-style:active {
  box-shadow: inset 5px 5px 10px #d1d1d1, inset -5px -5px 10px #ffffff;
  border: 2px solid red;
}

.our-neumorphism-style {
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}

.opponent-neumorphism-style {
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}

</style>