import type { PayloadAction } from '@reduxjs/toolkit';
import { createSelector, createSlice } from '@reduxjs/toolkit';
import type { PersistConfig } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import type { RootState } from '.';

//
// Initial State
//

export interface ConfigState {
  supportSourceListPageSize: number;
}

const buildInitialState = (): ConfigState => ({
  supportSourceListPageSize: 12,
});

//
// Slice
//
export const ConfigSlice = createSlice({
  name: 'auth',
  initialState: buildInitialState(),
  reducers: {
    setSupportedSourceListPageSize(state, action: PayloadAction<number>) {
      state.supportSourceListPageSize = action.payload;
    },
  },
});

//
// Actions & Selectors
//
const selectConfigState = (state: RootState) => state.config;
const selectSupportedSourceListPageSize = createSelector(
  selectConfigState,
  (state) => state.supportSourceListPageSize
);

export const Config = {
  action: ConfigSlice.actions,
  select: {
    supportedSourceListPageSize: selectSupportedSourceListPageSize,
  },
};

//
// Persist Config
//
const blacklist: Array<keyof ConfigState> = [
  // items to exclude from local storage
];

export const configPersistConfig: PersistConfig<ConfigState> = {
  key: 'config',
  version: 1,
  storage,
  blacklist,
};
