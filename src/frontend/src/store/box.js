export default {
  namespaced: true,
  state: {
    selectedBox: null,
    selectedImage: null,
    boxImages: []
  },
  mutations: {
    setSelectedBox(state, box) {
      state.selectedBox = box
    },
    setSelectedImage(state, image) {
      state.selectedImage = image
    },
    insertImageToBox(state) {
        if (state.selectedBox && state.selectedImage) {
          state.boxImages[state.selectedBox - 1] = state.selectedImage;
          state.selectedBox = null;
          state.selectedImage = null;
        }
    },
  }
}
