import { createStore } from 'vuex';

export default createStore({
  state: {
    selectedImage: null
  },
  mutations: {
    selectImage(state, imageIndex) {
      state.selectedImage = state.selectedImage === imageIndex ? null : imageIndex;
    }
  }
});
