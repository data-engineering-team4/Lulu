<template>
  <div class="ban-pick">
    <div class="ban-pick-page">
      <div class="ban-pick-board">
        <div class="title-section">
         <div class="custom-light-font" style="display: inline-block;">BanPick&nbsp;</div>
         <div class="custom-font" style="display: inline-block;">DashBoard&nbsp;&nbsp;&nbsp;</div>
          <div class="real-time custom-light-font">&nbsp;&nbsp;&nbsp;real-time&nbsp;recommend&nbsp;&nbsp;&nbsp;&nbsp;</div>
        </div>
        <div class="section">
          <div class="left-section">
            <div class="lane-circle" style="margin-top: 75%">
              <img src="@/assets/top.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle">
              <img src="@/assets/jug.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle">
              <img src="@/assets/mid.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle">
              <img src="@/assets/bottom.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle">
              <img src="@/assets/sup.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
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
          <div class="champion-buttons-husks">
          <div class="champion-buttons">
            <ChampionButton :selectedChampionIndex="selectedChampionIndex" :disabledChampions="disabledChampions" @select-champion="selectChampion"/>
          </div>
            </div>
          <div>
            <button @click="submit" class="submit custom-font" :class="{ 'enabled': isSubmitEnabled }" :disabled="!isSubmitEnabled">챔피언 선택</button>
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
      boxChampionIndices: Array(10).fill(null),
    };
  },
  computed: {
    ...mapState('box', ['selectedBox', 'selectedImage']),
    isSubmitEnabled() {
      return this.selectedBox && this.selectedImage;
    }
  },
  methods: {
    // ...mapMutations('box', ['setSelectedBox']),
    ...mapMutations('box', ['setSelectedBox', 'setSelectedImage']),

    selectChampion(imageUrl, index) {
      if (this.disabledChampions.includes(index)) return;
      this.selectedChampionIndex = index;
      this.setSelectedImage(imageUrl);
    },
    selectBox(box) {
      this.disabledChampions = this.disabledChampions.filter(i => i !== this.boxChampionIndices[box - 1]);
      this.setSelectedBox(box);
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
        this.boxChampionIndices[this.selectedBox - 1] = this.selectedChampionIndex;
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
.real-time{
  display: inline-block;
  font-size: 20px;
  border-radius: 25px;
background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
  padding: 5px;
}
.section {
  display: flex;
  align-items: flex-start;
  margin: 2%;
  }
.left-section{
  display: block;
  width: 5vw;
  height: 100%;
  padding-left: 0%;
  justify-content: center;
}
.lane-circle{
  width: 4vw;
  height: 8vh;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: auto;
  margin-top: 40%;
  margin-right: 5%;
  border-radius: 50%;
background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
}
.main-section{
  display: flex;
  align-items: flex-start;
  width: 50vw;
  margin-left: 1%;
  margin-right: 2%;
  margin-bottom: 4%;
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
  justify-content: center;

}
.champion-secction{
  margin: 1% 3% 3% 1%;
  width: 28vw;

}

.our-team-section {
  width: 20%;
  height: 80%;
  display: block;
  justify-content: center;
}

.opponent-team-section {
  width: 20%;
  height: 100%;
  display: block;
  justify-content: center;

}
.submit {
  width: 15vw;
  height: 3vw;
  margin-top: 5vh;
  font-size: x-large;
  border: 0px;
border-radius: 25px;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;

}
.submit.enabled {
  background-color: #6438af;
  color: #e4d7f5;
}

.our-lane-box {
  height: 10vh;
  width: 5vw;
  margin: 10% 0px 0% 20%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.our-lane-box.selected {
  border: 5px solid #4c00ff;
}

.opponent-lane-box {
  height: 10vh;
  width: 5vw;
  margin: 10% 20% 0% 0%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.opponent-lane-box.selected {
  border: 5px solid #ff0066;
}

.lane-img {
  height: 70%;
  width: 100%;
  object-fit: contain;
  border-radius: 20px;
}
.champion-buttons-husks{
  height: 46vh;
    width: 28vw;
  border-radius: 25px;
  padding-top: 3%;
background: #eeeeee;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;
}

.champion-buttons {
  height: 40vh;
  overflow-y: scroll;
  display: block;
  justify-content: center;
  padding: 0% 0% 5% 0%;
  width: 28vw;
  justify-content: center;


  &::-webkit-scrollbar {
    width: 10px; /* 스크롤바 너비 */
  }

  &::-webkit-scrollbar-track {
    background: #eeeeee; /* 스크롤바 배경색 */
  }

  &::-webkit-scrollbar-thumb {
    background: #888; /* 스크롤바 색 */
    border-radius: 8px; /* 둥근 모서리 */
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #9752ff; /* 스크롤바 마우스 오버 색 */
  }
}

.our-neumorphism-style:active {
  box-shadow: inset 5px 5px 10px #d1d1d1, inset -5px -5px 10px #ffffff;
  border: 2px solid #4c00ff;
}

.opponent-neumorphism-style:active {
  box-shadow: inset 5px 5px 10px #d1d1d1, inset -5px -5px 10px #ffffff;
  border: 2px solid #ff0066;
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