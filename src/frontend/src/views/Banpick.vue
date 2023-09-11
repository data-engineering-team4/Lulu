<template>
  <div class="ban-pick">
    <div class="ban-pick-page">
      <div class="ban-pick-board">
        <div class="title-section">
          <div class="custom-light-font" style="display: inline-block;">BanPick&nbsp;</div>
          <div class="custom-font" style="display: inline-block;">DashBoard&nbsp;&nbsp;&nbsp;</div>
          <div class="sectionButton">
            <div v-if="showSection == false" class="sectionButton1 custom-light-font2" @click="showRecommendSection">
              <span>분석으로 전환</span>
            </div>
            <div v-else class="sectionButton2 custom-light-font2" @click="showRecommendSection">
              <span>티어로 전환</span>
            </div>
          </div>
        </div>
        <div class="section">
          <div class="left-section">
            <div class="lane-circle" :style="{ 'margin-top': '12vh', filter: laneCircles[0] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(0),updateUserLane(0)">
              <img src="@/assets/bottom.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[1] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(1),updateUserLane(1)">
              <img src="@/assets/jug.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[2] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(2),updateUserLane(2)">
              <img src="@/assets/mid.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[3] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(3),updateUserLane(3)">
              <img src="@/assets/top.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
            <div class="lane-circle" :style="{ filter: laneCircles[4] ? 'hue-rotate(360deg)' : 'grayscale(100%)' }" @click="selectCircle(4),updateUserLane(4)">
              <img src="@/assets/sup.png" style="max-width: 60%;max-height: 60%; filter: hue-rotate(230deg); ">
            </div>
          </div>
          <div class="main-section">
            <div class="our-team-section" @click="toggleOurTeamSelection">
            <h2 :style="{ color: ourTeamSelected ? '#4c00ff' : '#b899ff' }" :class="[ourTeamSelected ? 'custom-font' : 'custom-light-font', 'custom-font']">&nbsp;&nbsp;&nbsp;우리팀</h2>
            <div v-for="(box, index) in our_boxes" :key="box" @click="selectBox(box)" :class="['our-lane-box', box === selectedBox ? 'selected' : '', selectedOurLaneIndex === index ? 'selected-our-lane' : '', 'our-neumorphism-style'] ">
                <img v-if="boxImages[index]" :src="boxImages[index]" alt="Champion Image" class="lane-img"/>
                <span class="position-label custom-font" :style="getLabelStyle(index)">I'm<br>{{ getPositionLabel(index)}}</span>
            </div>
        </div>
        <div class="champion-section">
          <div class="team-header" style="height: 30%;">
            <div class="button-container">
              <div class = "filter" style="flex: 1; height: 30%;">
                <button class="button1" :class="{ active: buttons[0] }" @click="toggleButton(0)">
                  <img src="@/assets/bottom.png" style="max-width: 100%; max-height: 100%;" />
                </button>
                <button class="button1" :class="{ active: buttons[1] }" @click="toggleButton(1)">
                  <img src="@/assets/jug.png" style="max-width: 100%; max-height: 100%;" />
                </button>
                <button class="button1" :class="{ active: buttons[2] }" @click="toggleButton(2)">
                  <img src="@/assets/mid.png" style="max-width: 100%; max-height: 100%;" />
                </button>
                <button class="button1" :class="{ active: buttons[3] }" @click="toggleButton(3)">
                  <img src="@/assets/top.png" style="max-width: 100%; max-height: 100%;" />
                </button>
                <button class="button1" :class="{ active: buttons[4] }" @click="toggleButton(4)">
                  <img src="@/assets/sup.png" style="max-width: 100%; max-height: 100%;" />
                </button>
              </div>
              <div style="flex: 2; height: 5%; display: flex; margin-right: 0; justify-content: space-between;">
                <div class = "pick" style="flex: 2; margin-top: 3%; margin-left: 5%;">
                  <h3 class="custom-font">챔피언을 선택하세요!</h3>
                </div>
                <div class = "tier" style="flex: 1.3; height: 100%; align-items: center; margin-top: 18%; margin-bottom: 0px;">
                  <div class="custom-dropdown" @click="toggleDropdown" style="width: 100%; height: 100%; padding-left: 0px; padding-right: 0px; align-items: center;">
                    <div v-if="selectedTier" class="tier-item" style="align-items: center; height: 100%;">
                      <img v-if="selectedTier === 'challenger'" src="@/assets/tier/challenger.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'grandmaster'" src="@/assets/tier/grandmaster.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'master'" src="@/assets/tier/master.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'diamond'" src="@/assets/tier/diamond.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'emerald'" src="@/assets/tier/emerald.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'platinum'" src="@/assets/tier/platinum.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'gold'" src="@/assets/tier/gold.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'silver'" src="@/assets/tier/silver.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'bronze'" src="@/assets/tier/bronze.webp" class="tier-icon" />
                      <img v-if="selectedTier === 'iron'" src="@/assets/tier/iron.webp" class="tier-icon" />
                      <span v-if="selectedTier === 'all'" class="tier-text0">{{ capitalizeFirstLetter }}</span>
                      <span v-else class="tier-text">{{ capitalizeFirstLetter }}</span>
                    </div>
                    <div v-else class="placeholder">티어를 선택하세요!</div>
                    <ul v-show="isDropdownOpen" class="dropdown-options">
                      <li @click="selectTier('all'), getTier()" class="tier-item">
                        <span class="tier-text0">All</span>
                      </li>
                      <li @click="selectTier('challenger'), getTier()" class="tier-item">
                        <img src="@/assets/tier/challenger.webp" class="tier-icon" />
                        <span class="tier-text">Challenger</span>
                      </li>
                      <li @click="selectTier('grandmaster'), getTier()" class="tier-item">
                        <img src="@/assets/tier/grandmaster.webp" class="tier-icon" />
                        <span class="tier-text">Grandmaster</span>
                      </li>
                      <li @click="selectTier('master'), getTier()" class="tier-item">
                        <img src="@/assets/tier/master.webp" class="tier-icon" />
                        <span class="tier-text">Master</span>
                      </li>
                      <li @click="selectTier('diamond'), getTier()" class="tier-item">
                        <img src="@/assets/tier/diamond.webp" class="tier-icon" />
                        <span class="tier-text">Diamond</span>
                      </li>
                      <li @click="selectTier('emerald'), getTier()" class="tier-item">
                        <img src="@/assets/tier/emerald.webp" class="tier-icon" />
                        <span class="tier-text">Emerald</span>
                      </li>
                      <li @click="selectTier('platinum'), getTier()" class="tier-item">
                        <img src="@/assets/tier/platinum.webp" class="tier-icon" />
                        <span class="tier-text">Platinum</span>
                      </li>
                      <li @click="selectTier('gold'), getTier()" class="tier-item">
                        <img src="@/assets/tier/gold.webp" class="tier-icon" />
                        <span class="tier-text">Gold</span>
                      </li>
                      <li @click="selectTier('silver'), getTier()" class="tier-item">
                        <img src="@/assets/tier/silver.webp" class="tier-icon" />
                        <span class="tier-text">Silver</span>
                      </li>
                      <li @click="selectTier('bronze'), getTier()" class="tier-item">
                        <img src="@/assets/tier/bronze.webp" class="tier-icon" />
                        <span class="tier-text">Bronze</span>
                      </li>
                      <li @click="selectTier('iron'), getTier()" class="tier-item">
                        <img src="@/assets/tier/iron.webp" class="tier-icon" />
                        <span class="tier-text">Iron</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="champion-buttons-husks">
          <div class="champion-buttons">
            <ChampionButton :selectedChampionIndex="selectedChampionIndex" :disabledChampions="disabledChampions" :selectedButtonIndex="selectedButtonIndex" :tierData="tierData" @select-champion="selectChampion" />
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
                  <div class="recommend-mastery-user"><input v-model="summonerName" @keyup.enter="search" class="mastery-summoner-name custom-font" type="text" placeholder="소환사명"></div>
                  <div><i @click="search" class="fas fa-search search-icon"></i> </div>
                </div>
                <div class="recommend-mastery-second">
                  <div class="recommend-mastery-lane">
                    <img class="mastery-lane" :src="recommendMasteryLaneContent ? require('@/assets/' + recommendMasteryLaneContent) : require('@/assets/unselect.png')" />
                  </div>
                  <div class="recommend-mastery-all">
                    <p v-if="championMastery.length > 0"></p>
                    <div class="champion-images">
                      <div v-for="(mastery, index) in championMastery" :key="mastery.championId">
                        <div v-if="index < 5">
                          <div v-if="userLane === null">
                            <img class="round-image" :src="getImage(getChampionName(mastery.championId))" />
                          </div>
                          <div v-if="userLane === 0">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                          <div v-if="userLane === 1">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                          <div v-if="userLane === 2">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                          <div v-if="userLane === 3">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                          <div v-if="userLane === 4">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                          <div v-if="userLane === 5">
                            <img class="round-image" :src="getImage(selectMastery[index])" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="showSection" class="recommend-section-table">
                <div class="recommend-section-first">
                  <div class="recommend-section-opponent-lane">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 2%;">상대 라이너</h3>
                    <div class="recommend-section-part" style="display: flex; align-items: center;">
                      <div v-for="item in opponent_lane_check_dicts" :key="item.championName" class="opponent-team-recommend" style="width: 33%; flex:1; flex-direction: column; align-items: center;">
                        <img :src="getImage(item.championName)" style="max-width: 80%;max-height: 80%;">
                        <div class="custom-font" style="margin-top:10%">{{ getMsg(item.championName) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="recommend-section-our-team">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 2%; ">상대팀 조합</h3>
                    <div class="recommend-section-part" style="display: flex; align-items: center;">
                      <div v-for="item in opponent_team_check_dicts" :key="item.championName" class="opponent-team-recommend" style="width: 33%; flex:1; flex-direction: column; align-items: center;">
                        <img :src="getImage(item.championName)" style="max-width: 80%;max-height: 80%;">
                        <div class="custom-font" style="margin-top:10%">{{ getMsg(item.championName) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="recommend-section-second">
                  <div class="recommend-section-all">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 0%;">우리팀 조합</h3>
                    <div class="recommend-section-part" style="display: flex; align-items: center;">
                      <div v-for="item in our_team_check_dicts" :key="item.championName" class="opponent-team-recommend" style="width: 33%; flex:1; flex-direction: column; align-items: center;">
                        <img :src="getImage(item.championName)" style="max-width: 80%;max-height: 80%;">
                        <div class="custom-font" style="margin-top:10%">{{ getMsg(item.championName) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="recommend-section-final">
                    <h3 class="custom-font" style="color:#9752ff; margin-bottom: 5%; margin-top: 0%;">전체 조합</h3>
                    <div class="recommend-section-part" style="display: flex; align-items: center;">
                      <div v-for="item in all_team_check_dicts" :key="item.championName" class="opponent-team-recommend" style="width: 33%; height:50%; flex:1; flex-direction: column; align-items: center;">
                        <img :src="getImage(item.championName)" style="max-width: 80%;max-height: 80%;">
                        <div class="custom-font" style="margin-top:10%">{{ getMsg(item.championName) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="summonerInfoLoaded" class="recommend-section-table">
                <div class = "filter3" style="align-items: center; width: 100%">
                  <div class="recommend-mastery-title custom-font" style="width:100%;">
                     숙련도 기반 프로 매칭
                    <button class="reset-button" @click="resetRecommendSection" style="margin-left: auto;">
                      <i class="fas fa-undo"></i>
                    </button>
                  </div>
                  <div style="margin-top: 2%; justify-content: center; height: 100%;">
                    <div class="gamer-card">
                      <div class="gamer-nickname">
                        <span v-if="!errorMessage">
                          {{ recommendedProgamer.team}}의 {{getProgamerPOS(recommendedProgamer.position)}}, {{ recommendedProgamer.name }} 선수
                        </span>
                        <span v-else>
                          {{ errorMessage }}
                        </span>
                      </div>
                      <div class="gamer-img" :style="getBackgroundStyle(recommendedProgamer.team)">
                        <img :src="getProgamerImage(recommendedProgamer.name)" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="recommend-section-table">
                <div class = "filter2" style="align-items: center; width: 100%;">
                  <div class="recommend-mastery-title custom-font" style="flex: 2; margin-top: 0; font-size: 120%;">추천 챔피언</div>
                  <div style="flex: 1.5; margin-right: 10%;">
                    <button class="button2" :class="{ active: buttons2[0] }" @click="filterButton(0)">
                      <img src="@/assets/bottom.png" style="max-width: 100%; max-height: 100%;" />
                    </button>
                    <button class="button2" :class="{ active: buttons2[1] }" @click="filterButton(1)">
                      <img src="@/assets/jug.png" style="max-width: 100%; max-height: 100%;" />
                    </button>
                    <button class="button2" :class="{ active: buttons2[2] }" @click="filterButton(2)">
                      <img src="@/assets/mid.png" style="max-width: 100%; max-height: 100%;" />
                    </button>
                    <button class="button2" :class="{ active: buttons2[3] }" @click="filterButton(3)">
                      <img src="@/assets/top.png" style="max-width: 100%; max-height: 100%;" />
                    </button>
                    <button class="button2" :class="{ active: buttons2[4] }" @click="filterButton(4)">
                      <img src="@/assets/sup.png" style="max-width: 100%; max-height: 100%;" />
                    </button>
                  </div>
                </div>
                <div style="margin-top: 2%; justify-content: center; height: 100%;">
                  <div class="tier-page">
                    <div style="height: 100%;">
                      <div v-if="buttons2[0] == true" style="height: 100%;border-radius: 20px;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in topData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 60%; height: 80%; flex: 0.7;" />
                            <div v-auto-font-size class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="buttons2[1] == true" style="height: 100%;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in jugData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 70%; height: 80%; flex: 0.7;" />
                            <div class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="buttons2[2] == true" style="height: 100%;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in midData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 70%; height: 80%; flex: 0.7;" />
                            <div class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="buttons2[3] == true" style="height: 100%;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in botData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 70%; height: 80%; flex: 0.7;" />
                            <div class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="buttons2[4] == true" style="height: 100%;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in supData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 70%; height: 80%; flex: 0.7;" />
                            <div class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="!buttons2.some(Boolean)" style="height: 100%;">
                        <div style="height: 100%;">
                          <div style="display: flex; height: 10%; align-items: center;">
                            <div style="flex: 1; width: 70%;"></div>
                            <div class="custom-font" style="flex: 1;">이름</div>
                            <div class="custom-font" style="flex: 1;">픽률</div>
                            <div class="custom-font" style="flex: 1;">승률</div>
                            <div class="custom-font" style="flex: 1;">벤률</div>
                          </div>
                          <div v-for="(item, index) in allData.slice(0, 5)" :key="index" style="display: flex; height: 17.5%; align-items: center; border: 1px solid #ccc;">
                            <img class="round-image" :src="getImage(getChampionName(item.champion_id))" style="width: 70%; height: 80%; flex: 0.7;" />
                            <div class="custom-light-font" style="flex: 1;">{{ enKr[item.champion_name] }}</div>
                            <div class="custom-light-font" style="flex: 1;">{{ parseFloat(item.pick_rate).toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.win_rate.toFixed(2) }}%</div>
                            <div class="custom-light-font" style="flex: 1;">{{ item.ban_rate.toFixed(2) }}%</div>
                          </div>
                        </div>
                      </div>
                    </div>
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
      currentTimestamp: 0,
      is_enable_produce: 0,
      all_team_check_dicts:[],
      our_team_check_dicts:[],
      opponent_team_check_dicts:[],
      opponent_lane_check_dicts:[],
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
      },
      championMastery: [],
      errorMessage: '',
      recommendedProgamer: {},
      summonerInfoLoaded: false,
      championMapping: {},
      buttons: [false, false, false, false, false],
      buttons2: [false, false, false, false, false],
      selectedButtonIndex: null,
      userLane: null,
      masteryId: [],
      masteryName: [],
      masteryTop: [],
      masteryJug: [],
      masteryMid: [],
      masteryBot: [],
      masterySup: [],
      championTop: {},
      championJug: {},
      championMid: {},
      championBot: {},
      championSup: {},
      selectMastery: [],
      selectedTier: 'all',
      selectedPosition: 'TOP',
      isDropdownOpen: false,
      showSection: false,
      tierData: {},
      allData: [],
      topData: [],
      jugData: [],
      midData: [],
      botData: [],
      supData: [],
      enKr: {},
      obj: {},
      gamerHovered: false,
    };
  },
  watch: {
    userLane(index) {
      if (index == 0) {
        this.selectMastery = this.masteryTop;
      }
      if (index == 1) {
        this.selectMastery = this.masteryJug;
      }
      if (index == 2) {
        this.selectMastery = this.masteryMid;
      }
      if (index == 3) {
        this.selectMastery = this.masteryBot;
      }
      if (index == 4) {
        this.selectMastery = this.masterySup;
      }
      if (index == 5) {
        this.selectMastery = this.masteryName;
      }
    },
    selectTier(tier) {
      if (this.selectedTier == tier) {
        this.isDropdownOpen = false;
      }
    }
  },
  computed: {
    ...mapState('box', ['selectedBox', 'selectedImage']),
    isSubmitEnabled() {
      return this.selectedBox && this.selectedImage;
    },
    capitalizeFirstLetter() {
      if (this.selectedTier) {
        return this.selectedTier.charAt(0).toUpperCase() + this.selectedTier.slice(1);
      } else {
        return "";
      }
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

  if (this.is_enable_produce === 1 && this.teamInfo.myLane !== -1) {
    axios.post('/banpick/produce', this.teamInfo)
      .then(response => {
        console.log('Data sent successfully11', response);

        const tableCheck = response.data.table_check;
        this.all_team_check_dicts = response.data.all_team_check_dicts;
        this.our_team_check_dicts = response.data.our_team_check_dicts;
        this.opponent_team_check_dicts = response.data.opponent_team_check_dicts;
        this.opponent_lane_check_dicts = response.data.opponent_lane_check_dicts;
        const currentTimestamp = response.data.currentTimestamp;

        const kindList = [];

        if (tableCheck.includes("1")) kindList.push("allteam");
        if (tableCheck.includes("2")) kindList.push("ourteam");
        if (tableCheck.includes("3")) kindList.push("opponentteam");
        if (tableCheck.includes("4")) kindList.push("opponentlane");

        const requestData = { kinds: kindList, timestamp: currentTimestamp };

        if (kindList.length > 0) {
          console.log("consume");
          axios.post('/banpick/consume', requestData)
            .then(response => {
              response.data.data.forEach((obj) => {
                const key = Object.keys(obj)[0];
                if (kindList.includes(key)) {
                  if (key.startsWith('allteam')) {
                    const tmp=  Object.values(obj[key]);
                    const tmp2 = []
                    for (let i=0; i<3; i++){
                      tmp2.push({"championName":tmp[i]});
                    }
                    this.all_team_check_dicts = tmp2;
                  }
                  if (key.startsWith('ourteam')) {
                    const tmp=  Object.values(obj[key]);
                    const tmp2 = []
                    for (let i=0; i<3; i++){
                      tmp2.push({"championName":tmp[i]});
                    }
                    this.our_team_check_dicts = tmp2;
                  }
                  if (key.startsWith('opponentteam')) {
                    const tmp=  Object.values(obj[key]);
                    const tmp2 = []
                    for (let i=0; i<3; i++){
                      tmp2.push({"championName":tmp[i]});
                    }
                    this.opponent_team_check_dicts = tmp2;
                  }
                  if (key.startsWith('opponentlane')) {
                    const tmp=  Object.values(obj[key]);
                    const tmp2 = []
                    for (let i=0; i<3; i++){
                      tmp2.push({"championName":tmp[i]});
                    }
                    this.opponent_lane_check_dicts = tmp2;
                  }
                }
              });

            })

            .catch(error => {
              console.log('Error in consume call', error);
            });
        }
      })
      .catch(error => {
        console.log('Error sending data', error);
      });
  }
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
    getLabelStyle(index) {
      if (this.selectedLaneIndex === index) {
        return {
          color: '#eeeeee'
        };
      } else {
        return {
          color: 'transparent'
        };
      }
    },
    toggleButton(index) {
      if (this.buttons[index] == false) {
        this.buttons = [false, false, false, false, false]

        this.buttons[index] = !this.buttons[index];
        this.selectedButtonIndex = index;
      } else {
        this.buttons[index] = !this.buttons[index];
        this.selectedButtonIndex = null;
      }
    },
    filterButton(index) {
      if (this.buttons2[index] == false) {
        this.buttons2 = [false, false, false, false, false]

        this.buttons2[index] = !this.buttons2[index];
      } else {
        this.buttons2[index] = !this.buttons2[index];
      }
    },
    updateUserLane(index) {
      if (this.userLane === index) {
        this.userLane = 5;
      } else {
        this.userLane = index;
      }
    },
    toggleDropdown() {
      this.isDropdownOpen = !this.isDropdownOpen;
    },
    selectTier(tier) {
      this.selectedTier = tier;
    },
    showRecommendSection() {
      if (this.showSection == true) {
        this.showSection = false
        this.is_enable_produce = 0
      } else {
        this.showSection = true
        this.is_enable_produce = 1
      }
    },
    resetRecommendSection() {
      this.summonerName = '';
      this.summonerInfo = {};
      this.championMastery = [];
      this.recommendedProgamer = {};
      this.summonerInfoLoaded = false;
    },
    getBackgroundStyle(teamName) {
      if (teamName === 'KT Rolster') {
        return {backgroundColor: '#FF0A07'};
      } else if (teamName === 'T1') {
        return {backgroundColor: '#e4002b'};
      } else if (teamName === 'Gen.G') {
        return { backgroundColor: '#aa8a00'};
      } else if (teamName === 'Hanwha Life Esports') {
        return {backgroundColor: '#ff6b01'};
      } else if (teamName === 'Liiv SANDBOX') {
        return {backgroundColor: '#ffc600'};
      } else if (teamName === 'Dplus KIA') {
        return {backgroundColor: 'black'};
      } else if (teamName === 'Nongshim Red Force') {
        return {backgroundColor: '#de2027'};
      } else if (teamName === 'BRION') {
        return {backgroundColor: '#00492b'};
      } else if (teamName === 'DRX') {
        return {backgroundColor: '#5a8dff'};
      } else if (teamName === 'LNG') {
        return {backgroundColor: '#008ffd'};
      } else {
        return { backgroundColor: '#ffffff' };

      }
    },
    getMsg(championName) {
    const rank = this.getRank(championName);
    return rank === -2 ? "없음" : `${rank}위`;
    },
    getRank(name) {
      let dataToSearch;

      if (this.userLane == 0) {
        dataToSearch = this.topData;
      } else if (this.userLane == 1) {
        dataToSearch = this.jugData;
      } else if (this.userLane == 2) {
        dataToSearch = this.midData;
      } else if (this.userLane == 3) {
        dataToSearch = this.botData;
      } else if (this.userLane == 4) {
        dataToSearch = this.supData;
      }

      if (!dataToSearch || dataToSearch.length === 0) {
        return -1;
      }

      for (let i = 0; i < dataToSearch.length; i++) {
        if (dataToSearch[i].champion_name === name) {
          return i;
        }
      }

      return -2;
    },
    getTier() {
      axios
      .post(`/banpick/tier/${this.selectedTier}`, { timeout: 5000 })
        .then(response => {
          console.log('Data sent successfully', response);
          console.log('Data sent successfully', response.data);
          this.tierData = response.data[0];
          this.allData = response.data[0];
          this.topData = response.data[1];
          this.jugData = response.data[2];
          this.midData = response.data[3];
          this.botData = response.data[4];
          this.supData = response.data[5];
        })
        .catch(error => {
          console.log('Error sending data', error);
        });
    },
    search() {
      this.summonerInfo.summonerName = this.summonerName;
      axios
        .post('/banpick/search', this.summonerInfo, { timeout: 5000 })
        .then(response => {
          console.log('Data sent successfully', response);
          this.summonerName = response.data.summonerName;
          this.championMastery = response.data.championMastery;
          this.summonerInfoLoaded = true;
          this.recommendedProgamer = response.data.recommendedProgamer;
          this.masteryId = this.championMastery.map(mastery => mastery.championId);
          this.masteryName = this.masteryId.map(championId => this.championMapping[championId]);
          this.errorMessage = '';
          for (const masteryName of this.masteryName) {
            if (Object.values(this.championTop).includes(masteryName)) {
                this.masteryTop.push(masteryName);
            }
          }
          for (const masteryName of this.masteryName) {
            if (Object.values(this.championJug).includes(masteryName)) {
                this.masteryJug.push(masteryName);
            }
          }
          for (const masteryName of this.masteryName) {
            if (Object.values(this.championMid).includes(masteryName)) {
                this.masteryMid.push(masteryName);
            }
          }
          for (const masteryName of this.masteryName) {
            if (Object.values(this.championBot).includes(masteryName)) {
                this.masteryBot.push(masteryName);
            }
          }
          for (const masteryName of this.masteryName) {
            if (Object.values(this.championSup).includes(masteryName)) {
              this.masterySup.push(masteryName);
            }
          }
        })
        .catch(error => {
          console.log('Error sending data', error);
          this.errorMessage = '닉네임을 확인해주세요!';
          this.summonerInfoLoaded = [];
          this.championMastery = [];
          this.recommendedProgamer = {};
        });
    },
    getChampionName(championId) {

      return this.championMapping[championId] || "Unknown Champion";
    },
    getImage(imageName) {
      if (!imageName) return ''; // Handle if the image name is not provided

      return `https://ddragon.leagueoflegends.com/cdn/13.16.1/img/champion/${imageName}.png`;
    },
    getProgamerImage(imageName) {
      if (!imageName) return '';
      return require('@/assets/progamer/' + imageName + '.png');
    },
    getProgamerPOS(position) {
      if (position === 'MIDDLE') {
        return "MID";
      } else if (position === 'UTILITY') {
        return "SUPPORT"
      } else {
        return position;
      }
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
      if (this.is_enable_produce === 1)   {
      axios.post('/banpick/produce', this.teamInfo)
        .then(response => {
          console.log('Data sent successfully', response);

          const tableCheck = response.data.table_check;
          const all_team_check_dicts = response.data.all_team_check_dicts;
          const our_team_check_dicts = response.data.our_team_check_dicts;
          const opponent_team_check_dicts = response.data.opponent_team_check_dicts;
          const opponent_lane_check_dicts = response.data.opponent_lane_check_dicts;
          const currentTimestamp = response.data.currentTimestamp;

          const resultList = [all_team_check_dicts, our_team_check_dicts, opponent_team_check_dicts, opponent_lane_check_dicts];
          const kindList = [];

          if (tableCheck.includes("1")) kindList.push("allteam");
          if (tableCheck.includes("2")) kindList.push("ourteam");
          if (tableCheck.includes("3")) kindList.push("opponentteam");
          if (tableCheck.includes("4")) kindList.push("opponentlane");

          const requestData = { kinds: kindList ,timestamp: currentTimestamp };
          console.log(kindList)
          if (kindList.length > 0) {
                  console.log("consume")
                  axios.post('/banpick/consume', requestData)
                    .then(response => {
                      console.log(resultList)
                      console.log(response)
                    })
                    .catch(error => {
                      console.log('Error in consume call', error);
                    });
                }


        })
        .catch(error => {
          console.log('Error sending data', error);
        });
    }
    }
  },
  mounted() {
    this.getTier();

    fetch('/champion_dictionary.json')
      .then(response => response.json())
      .then(data => {
        this.championMapping = data;
      });
    fetch('/top.json')
      .then(response => response.json())
      .then(data => {
        this.championTop = data;
      });
    fetch('/jug.json')
      .then(response => response.json())
      .then(data => {
        this.championJug = data;
      });
    fetch('/mid.json')
      .then(response => response.json())
      .then(data => {
        this.championMid = data;
      });
    fetch('/bot.json')
      .then(response => response.json())
      .then(data => {
        this.championBot = data;
      });
    fetch('/sup.json')
      .then(response => response.json())
      .then(data => {
        this.championSup = data;
      });
    fetch('/champion_mapping_en_kr.json')
      .then(response => response.json())
      .then(data => {
        this.enKr = data;
      });
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
.custom-light-font2 {
  font-family: 'Doctum Light', sans-serif;
  font-size: 15px;
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
  display: flex;
  text-align: left;
  padding: 2% 0% 0% 3%;
  font-size: 30px;
  font-weight: 500;
  color: #9752ff;
  align-items: center;
}
.sectionButton {
  display: flex;
}
.sectionButton1{
  width: 150px;
  border-radius: 10px;
  background: #eeeeee;
  box-shadow: 3px 3px 1px #b7b7b7,
              -3px -3px 1px #ffffff;
  padding: 5px;
  text-align: center;
}
.sectionButton2{
  width: 150px;
  font-size: 20px;
  border-radius: 10px;
  background: #eeeeee;
  box-shadow: inset 3px 3px 1px #b7b7b7,
              inset -3px -3px 1px #ffffff;
  padding: 5px;
  text-align: center;
  color: dimgray;
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
  margin-right: 5px;
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

.champion-section{
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

.opponent-team-section > div {
  margin-left: 4px;
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
  position: relative;
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
  /* margin-top: 18%; */
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
  /* background-color: black; */
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
  display: flex;
  width: 23vw;
  height: 20%;
  padding-top: 3%;
  justify-content: center;
}
.recommend-mastery-title{
  width: 5vw;
  color: #9752ff;
  font-size: large;
  margin-top: 3%;
  margin-right: 3%;
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
  text-align: center;
  border: none;
  font-size: large;
  outline: none;
}
.recommend-mastery-second{
  display: flex;
  width: 23vw;
  height: 60%;
  margin: 2%;
  justify-content: center;
}

.recommend-mastery-second .recommend-mastery-lane{
  display: flex;
  width: 20%;
  height: 80%;
  justify-content: center;
  align-items: center;
  margin: 3%;
}
.mastery-lane{
  max-width: 100%;
  filter: hue-rotate(230deg);

}
.recommend-mastery-all{
  display: flex;
  width: 70%;
  height: 90%;
  margin-top: 2%;
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

.recommend-section-table .recommend-head > span {
  color: #9752ff;
}

.recommend-section-table .recommend-head {
  color: rgb(184, 153, 255);
}
.opponent-team-recommend{
  display: flex;
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
  display: flex;
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
.position-label{
  position: absolute;
}
.round-image {
  border-radius: 50%;
  width: 90%;
  height: 90%;
  margin: 3%;
}
.champion-images {
  display: flex;
  margin: 9% 5% 0;
}
.team-header {
  align-items: center;
}
.button-container {
  display: flex;
  justify-content: space-between;
}

.filter,
.pick
{
  display: flex;
  justify-content: space-between;
}

.filter {
  justify-content: flex-start; /* 왼쪽 정렬 */
  width: 35%;
  margin-left: 1%;
  margin-top: 13%;
  margin-bottom: 2%;
}

.filter2 {
  display: flex;
  justify-content: center;
  padding-top: 4%;
  padding-left: 5%;
}

.filter3 {
  width: 100%;
  align-items: center;
  flex: 2;
  padding-top: 2%;
  padding-left: 5%;
  font-size: 120%;
}

.pick {

  color: #9752ff;
}

.tier {
  width: 100%;
  margin-top: 10px;
  margin-bottom: 13%;
  text-align: center;
}

.button1 {
  filter: grayscale(100%);
  background: #eeeeee;
  box-shadow:  2px 2px 1px #b7b7b7,
              -2px -2px 1px #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: 30%;
  height: 80%;
  margin-left: 3%;
}
.button1.active {
  filter: hue-rotate(230deg);
  box-shadow: inset 1px 1px 2px #d1d1d1, inset -1px -1px 2px #ffffff;
}
.button2 {
  filter: grayscale(100%);
  background: #eeeeee;
  box-shadow:  2px 2px 1px #b7b7b7,
              -2px -2px 1px #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: 16%;
  margin-top: 7%;
  margin-left: 3%;
}
.button2.active {
  filter: hue-rotate(230deg);
  box-shadow: inset 1px 1px 2px #d1d1d1, inset -1px -1px 2px #ffffff;
}

.custom-dropdown {
  position: relative;
  align-items: center;
  cursor: pointer;
  border: 2px solid #ccc;
  border-radius: 5px;
  padding: 0.1rem 1rem;
  background: #e4d7f5;
  width: 100%;
  height: 70%;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.custom-dropdown:hover {
  border-color: #999;
}

.dropdown-options {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ccc;
  border-top: none;
  width: 100%;
  background-color: #f0f0f0;
  position: absolute;
  top: 100%;
  left: 0;
}

.dropdown-options li {
  cursor: pointer;
  border: 1px solid #ccc;
}

.dropdown-options li:hover {
  background-color: #e1dede;
}

.tier-item {
  display: flex;
  align-items: center;
}

.tier-icon {
  width: 18%;
  height: 18%;
  margin-left: 5%;
}

.tier-text0 {
  font-family: 'Player Title';
  margin-top: 3%;
  margin-bottom: 3%;
  flex-grow: 1;
}
.tier-text {
  font-family: 'Player Title';
  margin-right: 5%;
  flex-grow: 1;
}
.tier-page {
  width: 90%;
  height: 80%;
  margin-left: 5%;
  justify-content: center;
  background: linear-gradient(145deg, #d6d6d6, #ffffff);
  box-shadow:  3px 3px 4px #9b9b9b,
              -3px -3px 4px #ffffff;
}

.recommend-section-table .reset-button {
  filter: grayscale(100%);
  background: #eeeeee;
  box-shadow:  2px 2px 1px #b7b7b7,
              -2px -2px 1px #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.gamer-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 90%;
  height: 80%;
  justify-content: center;
  background: linear-gradient(145deg, #d6d6d6, #ffffff);
  box-shadow:  3px 3px 4px #9b9b9b,
              -3px -3px 4px #ffffff;
}

.gamer-card .gamer-nickname {
  font-family: 'Player Title';
}

.gamer-card .gamer-img img {
  overflow: hidden;
  max-width: 90%;
  max-height: 90%;
}
</style>