import { configureStore } from "@reduxjs/toolkit";

import { baseSlice } from "./api/base";

export const store = configureStore({
  reducer: {
    [baseSlice.reducerPath]: baseSlice.reducer
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware()
      .concat(baseSlice.middleware)
})
