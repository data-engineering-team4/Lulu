<template>
  <div class="champion-buttons-container">
    <div v-for="(image, index) in images" :key="index" class="champion-button" :class="{ disabled: disabledChampions.includes(this.changeIndex(index)) }" :style="{border: this.changeIndex(index) === selectedChampionIndex ? '8px solid #6438af' : '' }">
      <img :src="image" @click="changeImage(index)" style="max-width: 90%; max-height: 90%;" @mousemove="updateBoxPosition" @mouseenter="showBox(index)" @mouseleave="hideBox"/>
      <div v-if="isBoxVisible && hoveredIndex === index" class="image-box" :style="{ top: boxTop + 'px', left: boxLeft + 'px' }">
        <img :src="image" @click="changeImage(index)" style="max-width: 40%; max-height: 40%; float: left; margin-right: 10px;"/>
        <div style="font-size: 20px;">
          {{ champions_kr[champions[index+1]] }}
        </div>
        <div class="info-label-container">
          <div class="info-label1">
            <div>픽률</div>
            <div class="info-label2">{{ getPick(getId(champions[index+1])) !== 0 ? getPick(getId(champions[index+1])) + '%' : '표본 부족' }}</div>
          </div>
          <div class="info-label1">
            <div>승률</div>
            <div class="info-label2">{{ getWin(getId(champions[index+1])) !== 0 ? getWin(getId(champions[index+1])) + '%' : '표본 부족' }}</div>
          </div>
          <div class="info-label1">
            <div>벤률</div>
            <div class="info-label2">{{ getBan(getId(champions[index+1])) !== 0 ? getBan(getId(champions[index+1])) + '%' : '표본 부족' }}</div>
          </div>
        </div>
        <div class="info-label3">
          <div>유사한 챔피언</div>
          <div class="info-label4">{{ getMastery(champions_kr[champions[index+1]]) }}
            <div class="info-label5"><img :src="getImage(champions_en[masteryData.column_1])" /></div>
            <div class="info-label5"><img :src="getImage(champions_en[masteryData.column_2])" /></div>
            <div class="info-label5"><img :src="getImage(champions_en[masteryData.column_3])" /></div>
            <div class="info-label5"><img :src="getImage(champions_en[masteryData.column_4])" /></div>
            <div class="info-label5"><img :src="getImage(champions_en[masteryData.column_5])" /></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    selectedChampionIndex: {
      type: Number,
      required: true
    },
    disabledChampions: {
      type: Array,
      default: () => []
    },
    selectedButtonIndex: Object,
    tierData: {
      type: Array,
      default: () => []
    }
  },
  name: 'ChampionButton',
  data() {
    return {
      champions: {},
      champions2: {},
      specialImage: 'https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/Rumble.png',
      selectedImage: [],
      images: [],
      isBoxVisible: false,
      hoveredIndex: null,
      boxTop: 0,
      boxLeft: 0,
      champions_kr: {},
      champions_en: {},
      requestedMastery: false,
      masteryData: '',
      pick: 0,
      champions_map: {},
      id: '',
      championsIndex: {},
    };
  },
  watch: {
    selectedButtonIndex(newIndex) {
      let apiEndpoint = '/champions.json';

      if (newIndex === 0) {
        apiEndpoint = '/top.json';
        // this.disabledChampions = [];
      }
      if (newIndex === 1) {
        apiEndpoint = '/jug.json';
      }
      if (newIndex === 2) {
        apiEndpoint = '/mid.json';
      }
      if (newIndex === 3) {
        apiEndpoint = '/bot.json';
      }
      if (newIndex === 4) {
        apiEndpoint = '/sup.json';
      }

      fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
          this.champions = data;
          this.images = Object.values(this.champions).map(name => `https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/${name}.png`);
          this.selectedImage = this.images.map(() => false);
        });
    }
  },
  methods: {
    changeIndex(index) {
      const championValues = Object.values(this.champions);
      if (index >= 0 && index < championValues.length) {
      const foundIndex = Object.keys(this.championsIndex).find(key => this.championsIndex[key] === championValues[index]);
      return foundIndex-1;
      }
    },
    changeImage(index) {
      if (this.disabledChampions.includes(this.changeIndex(index))) return;
      this.$emit('select-champion', this.images[index], this.changeIndex(index));
    },
    updateBoxPosition(event) {
      this.boxTop = event.clientY + 10; // 10 픽셀 위로 이동
      this.boxLeft = event.clientX + 10; // 10 픽셀 오른쪽으로 이동
    },
    showBox(index) {
      this.hoveredIndex = index;
      this.isBoxVisible = true;
    },
    hideBox() {
      this.hoveredIndex = null;
      this.isBoxVisible = false;
      this.requestedMastery = false;
    },
    getMastery(championName) {
      if (this.requestedMastery) return;

      this.requestedMastery = true;

      axios.get(`/champion-info?champion_name=${championName}`)
        .then(response => {
          const masteryData = response.data; // Get the specific column from the response
          this.masteryData = masteryData; // Set the fetched mastery data to the component's data property
        })
        .catch(error => {
          console.error('Error fetching champion mastery data:', error);
        });
    },
    getImage(imageName) {
      if (!imageName) return ''; // Handle if the image name is not provided

      return `https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/${imageName}.png`;
    },
    selectLaneButton() {
      this.$emit('lane', 'selectedLaneInfo'); // 선택한 라인 정보를 이벤트와 함께 전달
    },
    getId(champ) {
      const foundId = Object.keys(this.champions_map).find(key => this.champions_map[key] === champ);

      if (foundId) {
        this.id = foundId;
        return this.id;
      } else {
        this.id = '0';
        return this.id;
      }
    },
    getPick(id) {
      for (let i = 0; i < this.tierData.length; i++) {
        if (this.tierData[i].champion_id == id) {
          const pickRate = this.tierData[i].pick_rate.toFixed(2);
          return parseFloat(pickRate);
        }
      }
      return 0;
    },
    getWin(id) {
      for (let i = 0; i < this.tierData.length; i++) {
        if (this.tierData[i].champion_id == id) {
          const winRate = this.tierData[i].win_rate.toFixed(2);
          return parseFloat(winRate);
        }
      }
      return 0;
    },
    getBan(id) {
      for (let i = 0; i < this.tierData.length; i++) {
        if (this.tierData[i].champion_id == id) {
          const banRate = this.tierData[i].ban_rate.toFixed(2);
          return parseFloat(banRate);
        }
      }
      return 0;
    }
  },
  mounted() {
    let apiEndpoint = '/champions.json';
    
    fetch(apiEndpoint)
      .then(response => response.json())
      .then(data => {
        this.champions = data;
        this.images = Object.values(this.champions).map(name => `https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/${name}.png`);
        this.selectedImage = this.images.map(() => false);
      });

    fetch('/champion_mapping_en_kr.json')
      .then(response => response.json())
      .then(data => {
        this.champions_kr = data;
      });

    fetch('/champion_mapping_kr_en.json')
      .then(response => response.json())
      .then(data => {
        this.champions_en = data;
      });

    fetch('/champion_dictionary.json')
      .then(response => response.json())
      .then(data => {
        this.champions_map = data;
      });

    fetch('/champions.json')
      .then(response => response.json())
      .then(data => {
        this.championsIndex = data;
      });

  }
}
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
  box-shadow:  2px 2px 2px #b7b7b7, -2px -2px 2px #ffffff;
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
.image-box {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 5px;
  border-radius: 5px;
  font-size: 12px;
  top: 0;
  left: 0;
  width: 20%;
  height: 20%;
}
.info-label-container {
  margin-top: 5px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.info-label1 {
  margin-top: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  font-size: 100%;
  flex-direction: column;
}
.info-label2 {
  margin-top: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  font-size: 150%;
  flex-direction: column;
}
.info-label3 {
  margin-top: 7%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 100%;
  flex-direction: column;
}
.info-label4 {
  margin-top: 3%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 100%;
}
.info-label5 {
  margin: 0px 10px 0px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 20%;
  height: 20%;
}
</style>
