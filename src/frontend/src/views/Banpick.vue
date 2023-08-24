<template>
  <div class="ban-pick-page">
    <div class="team-section">
      <div class="lanes">
        <div class="team">우리팀</div>
        <div v-for="lane in lanes" :key="lane.name" class="lane">
          <img :src="lane.image" :alt="lane.name" class="lane-image" />
        </div>
      </div>
      <div class="champion-buttons">
        <ChampionButton />
      </div>
      <div class="lanes">
        <div class="team">상대팀</div>
        <div v-for="lane in lanes" :key="lane.name" class="lane">
          <img :src="lane.image" :alt="lane.name" class="lane-image" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChampionButton from '@/components/ChampionButton.vue';

export default {
  name: 'BanPickPage',
  components: {
    ChampionButton,
  },
  data() {
    return {
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
  methods: {
    selectLane(lane) {
      this.selectedLane = lane;
    },
  },
};

</script>
<style>
.ban-pick-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5% 10%;
}

.team-section {
  display: flex;
  align-items: flex-start;
}

.team {
  padding: 50px;
  font-size: 40px;
  display: block;
}

.lanes {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lane {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lane-image {
  width: 100%;
  height: 100%;
}

.champion-buttons {
  padding: 20px;
  height: 70vh;
  overflow-y: scroll;
}

</style>