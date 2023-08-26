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
            <div class="lane-circle" :style="{ 'margin-top': '12vh', filter: laneCircles[0] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(0)">
              <img src="@/assets/bottom.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[1] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(1)">
              <img src="@/assets/jug.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[2] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(2)">
              <img src="@/assets/mid.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[3] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(3)">
              <img src="@/assets/top.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[4] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(4)">
              <img src="@/assets/sup.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
          </div>
          <div class="main-section">
            <div class="our-team-section" @click="toggleOurTeamSelection">
            <h2 :style="{ color: ourTeamSelected ? '#4c00ff' : '#b899ff' }" :class="[ourTeamSelected ? 'custom-font' : 'custom-light-font', 'custom-font']">&nbsp;&nbsp;&nbsp;우리팀</h2>
            <div v-for="(box, index) in our_boxes" :key="box" @click="selectBox(box)" :class="['our-lane-box', box === selectedBox ? 'selected' : '', selectedOurLaneIndex === index ? 'selected-our-lane' : '', 'our-neumorphism-style'] ">
              <img v-if="boxImages[index]" :src="boxImages[index]" alt="Champion Image" class="lane-img"/>
               <span class="position-label custom-font" style="color: #eeeeee">I'm<br>{{ getPositionLabel(index)}}</span>
            </div>
        </div>
        <div class="champion-secction">
          <h5 class="custom-font" style="color: #9752ff; margin-top: 13.5%; margin-bottom: 1%">챔피언을 선택하세요!</h5>
          <div class="champion-buttons-husks">
          <div class="champion-buttons">
            <ChampionButton :selectedChampionIndex="selectedChampionIndex" :disabledChampions="disabledChampions" @select-champion="selectChampion"/>
          </div>
            </div>
          <div>
            <button @click="submit" class="submit custom-font" :class="{ 'enabled': isSubmitEnabled }" :disabled="!isSubmitEnabled">챔피언 선택</button>
          </div>
        </div>
            <div class="opponent-team-section" @click="toggleOpponentTeamSelection">
              <h2 :style="{ color: opponentTeamSelected ? '#ff0066' : '#b899ff' }" :class="[opponentTeamSelected ? 'custom-font' : 'custom-light-font', 'custom-font']">상대팀&nbsp;&nbsp;&nbsp;&nbsp;</h2>
              <div v-for="(box, index) in opponent_boxes" :key="box" @click="selectBox(box)" :class="['opponent-lane-box', box === selectedBox ? 'selected' : '', 'opponent-neumorphism-style']">
            <img v-if="boxImages[index+5]" :src="boxImages[index+5]" alt="Champion Image" class="lane-img"/>
          </div>
        </div>
          </div>
          <div class="right-section">
            <div class="recommend-section">
              <div class="recommend-section-mastery">
                <div class="recommend-mastery-first">
                  <div class="recommend-mastery-title custom-font">숙련도</div>
                  <div class="recommend-mastery-user"><input v-model="summonerName" class="mastery-summoner-name custom-font" type="text" placeholder="소환사명" style="text-align: center"></div>
                  <div><i @click="search" class="fas fa-search search-icon"></i> </div>
                </div>
                <div class="recommend-mastery-second">
                  <div class="recommend-mastery-lane">
                     <img class="mastery-lane" :src="recommendMasteryLaneContent ? require('@/assets/' + recommendMasteryLaneContent) : require('@/assets/unselect.png')" />
                  </div>
                  <div class="recommend-mastery-all">dd</div>
                </div>
              </div>
              <div class="recommend-section-table">
                <div class="recommend-section-first">
                  <div class="recommend-section-opponent-lane">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 2%;">상대 라이너</h3>
                    <div class="recommend-section-part">챔피언초상화,이름,티어 3개 </div>
                  </div>
                  <div class="recommend-section-our-team">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 2%; ">우리팀 조합</h3>
                    <div class="recommend-section-part">챔피언초상화,이름,티어 3개</div>
                  </div>
                </div>
                <div class="recommend-section-second">
                  <div class="recommend-section-all">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 0%;">전체 조합</h3>
                    <div class="recommend-section-part">챔피언초상화,이름,티어 3개</div>
                  </div>
                  <div class="recommend-section-final">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 0%;">최종 조합</h3>
                    <div class="recommend-section-part">챔피언초상화,이름,티어 3개 숙련도 고려</div>
                  </div>
                </div>
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
import axios from 'axios';

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
      selectedChampionIndex: {
        type: Number,
        default: 0
      },
      boxImages: Array(10).fill(null),
      disabledChampions: [],
      boxChampionIndices: Array(10).fill(null),
      laneCircles: Array(5).fill(false),
      selectedLaneIndex: null,
      recommendMasteryLaneContent: null,
      masteryLaneImage: 'unselect.png',
      laneContent: ['bottom.png', 'jug.png', 'mid.png', 'top.png', 'sup.png'
      ],
      unselectImage: require('@/assets/unselect.png'),
      selectedOurLaneIndex: null,
      teamInfo: {
        ourTeam: {},
        opponentTeam: {},
        myLane: -1
      },
      summonerName:'',
      summonerInfo:{
        summonerName: ''
      }
    };
  },
  computed: {
    ...mapState('box', ['selectedBox', 'selectedImage']),
    isSubmitEnabled() {
      return this.selectedBox && this.selectedImage;
    }
  },
  methods: {
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
    toggleOurTeamSelection() {
      this.ourTeamSelected = true;
      this.opponentTeamSelected = false;
    },
    toggleOpponentTeamSelection() {
      this.ourTeamSelected = false;
      this.opponentTeamSelected = true;
    },
    selectCircle(index) {
      if (this.selectedLaneIndex === index) {
        this.laneCircles = Array(5).fill(false);
        this.selectedLaneIndex = null;
        this.selectedOurLaneIndex = null;
        this.teamInfo.myLane = -1;
      } else {
        this.laneCircles = this.laneCircles.map((selected, idx) => idx === index ? true : false);
        this.selectedLaneIndex = index;
        this.selectedOurLaneIndex = index;
        this.teamInfo.myLane = this.selectedLaneIndex;
      }
      this.updateRecommendMasteryLane();
      axios.post('http://localhost:8000/banpick/produce', this.teamInfo)
        .then(response => {
          console.log('Data sent successfully', response);
        })
        .catch(error => {
          console.log('Error sending data', error);
        });
    },
    updateRecommendMasteryLane() {
      if (this.selectedLaneIndex !== null) {
        this.recommendMasteryLaneContent = this.laneContent[this.selectedLaneIndex];
      } else {
        this.recommendMasteryLaneContent = null;
        this.masteryLaneImage = 'unselect.png'
      }
    },
    getPositionLabel(index) {
      switch (index) {
        case 0:
          return "TOP";
        case 1:
          return "JUG";
        case 2:
          return "MID";
        case 3:
          return "BOT";
        case 4:
          return "SUP";
        default:
          return "";
      }}
    ,
    search(){
      this.summonerInfo.summonerName = this.summonerName
      axios.post('http://localhost:8000/banpick/search', this.summonerInfo)
        .then(response => {
          console.log('Data sent successfully', response);
        })
        .catch(error => {
          console.log('Error sending data', error);
        });
    },
    submit() {

      if (this.selectedBox && this.selectedImage) {
        this.boxImages[this.selectedBox - 1] = this.selectedImage;
        this.boxChampionIndices[this.selectedBox - 1] = this.selectedChampionIndex;
        if (this.ourTeamSelected) {
            this.teamInfo.ourTeam[this.selectedBox] = this.selectedChampionIndex;
          } else if (this.opponentTeamSelected) {
            this.teamInfo.opponentTeam[this.selectedBox] = this.selectedChampionIndex;
          }
        this.setSelectedBox(null);
        this.setSelectedImage(null);
        this.disabledChampions.push(this.selectedChampionIndex);
        this.selectedChampionIndex = null;
      } else {
        alert('?!!!')
      }

      axios.post('http://localhost:8000/banpick/produce', this.teamInfo)
        .then(response => {
          console.log('Data sent successfully', response);
        })
        .catch(error => {
          console.log('Error sending data', error);
        });
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
  margin-top: 32%;
  margin-right: 5%;
  border-radius: 50%;
background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
  cursor: pointer;
}
.main-section{
  display: flex;
  align-items: flex-start;
  width: 44vw;
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
  width: 15%;
  height: 80%;
  margin-top: 5%;
  display: block;
  justify-content: center;
}

.opponent-team-section {
  width: 15%;
  height: 100%;
  margin-top: 5%;
  display: block;
  justify-content: center;

}
.submit {
  width: 15vw;
  height: 3vw;
  margin-top: 2vh;
  font-size: large;
  border: 0px;
border-radius: 25px;
  background: #dddddd;
box-shadow:  5px 5px 3px #b7b7b7,
             -5px -5px 3px #ffffff;

}
.submit.enabled {
  cursor: pointer;
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
  cursor: pointer;
}
.our-lane-box.selected {
  border: 5px solid #4c00ff;
}

.selected-our-lane {
  background-color: #9752ff !important;
}

.opponent-lane-box {
  height: 10vh;
  width: 5vw;
  margin: 10% 0% 0% 0%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
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
  //margin-top: 18%;
  padding-top: 3%;
background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
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

.right-section{
  display: flex;
  height: 70vh;
  padding-left: 0%;
  justify-content: center;
}
.recommend-section{
  width: 25vw;
  height: 100%;
  //background-color: black;
  justify-content: center;

}
.recommend-section-mastery{
  width: 25vw;
  height: 30%;
  margin-bottom: 7%;
  justify-content: center;
    border-radius: 25px;
  background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
}

.recommend-mastery-first{
  width: 23vw;
  height: 20%;
  padding-top: 3%;
  margin-bottom: 3%;
  justify-content: center;
  display: flex;

}
.recommend-mastery-title{
  width: 5vw;
  color: #9752ff;
  font-size: large;
  margin-top: 3%;
  margin-right: 2%;
}
.recommend-mastery-user{
  width: 12vw;
  border-radius: 25px;
background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
}
.mastery-summoner-name{
  width: 80%;
  height: 100%;
  background: transparent;
  border: none;
  font-size: large;
  outline: none;
}
.recommend-mastery-second{
  width: 23vw;
  height: 60%;
  margin-left: 4%;
  justify-content: center;
  display: flex;
}

.recommend-mastery-lane{
  width: 20%;
  height: 80%;
  margin-left: 4%;
  justify-content: center;
  margin-top: 5%;
}
.mastery-lane{
  width: 100%;
  filter: hue-rotate(230deg);

}
.recommend-mastery-all{
  width: 70%;
  height: 90%;
  margin-top: 2%;
  margin-left: 6%;
  justify-content: center;
border-radius: 25px;
background: linear-gradient(145deg, #d6d6d6, #ffffff);
box-shadow:  5px 5px 6px #9b9b9b,
             -5px -5px 6px #ffffff;
}
.recommend-section-table{
  width: 25vw;
  height: 60%;
  margin-bottom: 7%;
  justify-content: center;
  border-radius: 25px;
  background: #eeeeee;
box-shadow: inset 5px 5px 3px #b7b7b7,
            inset -5px -5px 3px #ffffff;
}

.recommend-section-first{
  width: 24vw;
  height: 48%;
  display: flex;
    margin-left: 0.5%;
  justify-content: center;
}
.recommend-section-second{
  width: 24vw;
  height: 48%;
  display: flex;
  margin-left: 2.5%;
  justify-content: center;
}
.recommend-section-opponent-lane{
  width: 45%;
  margin-right: 3%;
  margin-top: 3%;
}
.recommend-section-our-team{
  width: 45%;
  margin-top: 3%;
}
.recommend-section-all{
  width: 45%;
  margin-right: 3%;
  margin-top: 3%;
}
.recommend-section-final{
  width: 45%;
  margin-right: 3%;
  margin-top: 3%;
}
.recommend-section-part{
  width: 95%;
  height: 75%;
border-radius: 25px;
background: linear-gradient(145deg, #d6d6d6, #ffffff);
box-shadow:  5px 5px 6px #9b9b9b,
             -5px -5px 6px #ffffff;
  margin-left: 5%;
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
.search-icon {
  color: #6438af;
  font-size: 20px;
  margin-left: 80%;
  cursor: pointer;
  margin-top: 50%;
}
</style>